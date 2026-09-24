from rest_framework import generics
from rest_framework.views import APIView
from scraper.models import NewsArticle,ChangedNewsArticle,Source,Region,SearchWords,NewsImage
from .serializers import NewsArticleSerializer,SourceSerializer,RegionSerializer,\
NewsArticleMonthlySerializer,NewsArticleCountbyRegionSerializer,MostlySourcesRegionSerializer,\
    MostlyArticlesSourceSerializer,AllSourceCountSerializer,DailyArticleCountSerializer,DailyArticleCountryCountSerializer,\
        NewsArticleAccessSerializer,NewsArticleDetailSerializer,ChangedNewsArticleHistorySerializer

from rest_framework import status
from rest_framework.response import Response
import pandas as pd
from django.http import HttpResponse
from django.utils.timezone import now
from django.db.models import Count
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.db.models import Q
from tasks.api.views import generate_expected_token
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now
from django.utils.timezone import make_aware
import requests
from user.authentication import CustomTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from utils.photo_save import download_and_resize_image
import hashlib
from datetime import datetime


def generate_expected_token(salt="token"):
    current_time = datetime.now().strftime("%Y%m%d %H")

    inner_hash = hashlib.md5(current_time.encode()).hexdigest()

    final_hash = hashlib.md5((salt + inner_hash).encode()).hexdigest()

    return final_hash


class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = None

    def get_page_number(self, request, paginator):
        page = request.data.get('page', 1)
        return page if page else 1

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'count': self.page.paginator.count,
            'data': data
        }, status=status.HTTP_200_OK)



import operator        
from functools import reduce                                     


class NewsArticleListApiView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = NewsArticleAccessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        search = serializer.validated_data.get('search', None)
        publish_date_start = serializer.validated_data.get('publish_date_start', None)
        publish_date_end = serializer.validated_data.get('publish_date_end', None)
        source_id = serializer.validated_data.get('source_id', None)
        region_id = serializer.validated_data.get('region_id', None)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "message": "Invalid token",
                "status": "error",
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Cache açarı yarat
        cache_key = f"news_articles:{search}:{publish_date_start}:{publish_date_end}:{source_id}:{region_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        queryset = NewsArticle.objects.all()

        if publish_date_start:
            queryset = queryset.filter(news_shared_date__gte=publish_date_start)

        if publish_date_end:
            queryset = queryset.filter(news_shared_date__lte=publish_date_end)

        if search:
            search_terms = [term.strip() for term in search.split(',') if term.strip()]
            if search_terms:
                query = reduce(
                    operator.and_,
                    [Q(title__icontains=term) | Q(content__icontains=term) for term in search_terms]
                )
                queryset = queryset.filter(query)

        if source_id:
            queryset = queryset.filter(source_id=source_id)

        if region_id:
            queryset = queryset.filter(source__region_id=region_id)

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = NewsArticleSerializer(page, many=True)
            response_data = paginator.get_paginated_response(serializer.data).data
        else:
            serializer = NewsArticleSerializer(queryset, many=True)
            response_data = {
                "status": "success",
                "count": queryset.count(),
                "data": serializer.data,
            }

        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data, status=status.HTTP_200_OK)


class NewsArticleSearchApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NewsArticleAccessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        search = serializer.validated_data.get('search', None)
        source_id = serializer.validated_data.get('source_id', None)
        region_id = serializer.validated_data.get('region_id', None)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                
                "message": "Invalid token",
                "status": "error",
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Cache açarı (son 10 nəticə üçün)
        cache_key = f"news_articles_latest:10:{search}:{source_id}:{region_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        queryset = NewsArticle.objects.all()

        if search:
            search_terms = [term.strip() for term in search.split(',') if term.strip()]
            if search_terms:
                query = reduce(
                    operator.and_,
                    [Q(title__icontains=term) | Q(content__icontains=term) for term in search_terms]
                )
                queryset = queryset.filter(query)

        if source_id:
            queryset = queryset.filter(source_id=source_id)

        if region_id:
            queryset = queryset.filter(source__region_id=region_id)

        queryset = queryset.order_by('-created_at')[:10]  # son 10 nəticə

        serializer = NewsArticleSerializer(queryset, many=True)
        response_data = {
            "status": "success",
            "data": serializer.data,
        }

        cache.set(cache_key, response_data, timeout=300)  
        return Response(response_data, status=status.HTTP_200_OK)


class NewsArticleDetailAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NewsArticleDetailSerializer(data=request.data)
        if serializer.is_valid():
           
            token = serializer.validated_data['token']
            article_id = serializer.validated_data['id']

            expected_token = generate_expected_token()
            if token != expected_token:
                return Response({
                    "message": "Invalid token",
                    "status": "error",
                }, status=status.HTTP_401_UNAUTHORIZED)

            try:
                article = NewsArticle.objects.select_related('source__region_id').get(id=article_id)

                source_data = None
                if article.source:
                    region = article.source.region_id
                    source_data = {
                        "id": article.source.id,
                        "name": article.source.name,
                        "link": article.source.link,
                        "region": {
                            "id": region.id if region else None,
                            "name": region.name if region else None
                        }
                    }

                base_url = "http://192.168.0.201:8000"

                main_image = article.images.filter(is_main=True).first()
                gallery_images = article.images.filter(is_main=False)

                article_data = {
                    "url": article.url,
                    "title": article.title,
                    "description": article.description,
                    "content": article.content,
                    "main_image_url": main_image.image_url if main_image else None,
                    "main_image_local": (
                        f"{base_url}{main_image.local_image_url.url}"
                        if main_image and main_image.local_image_url else None
                    ),
                    "gallery_images": [
                        {
                            "image_url": img.image_url,
                            "local_image_url": (
                                f"{base_url}{img.local_image_url.url}"
                                if img.local_image_url else None
                            )
                        } for img in gallery_images
                    ],
                    "news_shared_date": article.news_shared_date,
                    "created_at": article.created_at,
                    "source": source_data
                }

                changed_articles = article.changednewsarticles.order_by("-created_at")
                changed_data = []
                for c in changed_articles:
                    main_changed_image = c.images.filter(is_main=True).first()
                    gallery_changed_images = c.images.filter(is_main=False)

                    changed_data.append({
                        "title": c.title or article.title,
                        "description": c.description or article.description,
                        "content": c.content or article.content,
                        "main_image_url": main_changed_image.image_url if main_changed_image else None,
                        "main_image_local": (
                            f"{base_url}{main_changed_image.local_image_url.url}"
                            if main_changed_image and main_changed_image.local_image_url else None
                        ),
                        "gallery_images": [
                            {
                                "image_url": img.image_url,
                                "local_image_url": (
                                    f"{base_url}{img.local_image_url.url}"
                                    if img.local_image_url else None
                                )
                            } for img in gallery_changed_images
                        ],
                        "news_shared_date": c.news_shared_date or article.news_shared_date,
                        "created_at": c.created_at,
                        "source": source_data
                    })

                full_history = [article_data] + changed_data

                return Response({
                    "status": "success",
                    "data": full_history
                }, status=status.HTTP_200_OK)

            except NewsArticle.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Article not found"
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegionListApiView(APIView):
    def post(self, request):
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            
            token = serializer.validated_data['token']

            expected_token = generate_expected_token()
            if token != expected_token:
                return Response({
                    "status": "error",
                    "message": "Invalid token"
                }, status=status.HTTP_401_UNAUTHORIZED)

            regions = Region.objects.prefetch_related('sources').all()
            region_data = []
            for region in regions:
                sources = region.sources.all()
                source_list = [{"id": s.id,"name": s.name,"link": s.link,"created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S"),"type": s.type,}for s in sources]

                region_data.append({
                    "id": region.id,
                    "name": region.name,
                    "sources": source_list
                })

            return Response({
                "status": "success",
                "data": region_data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ExportNewsArticlesView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"detail": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        
        if len(date_str) == 7:  
            queryset = NewsArticle.objects.filter(news_shared_date__year=date_str[:4], news_shared_date__month=date_str[5:])
        else:  
            queryset = NewsArticle.objects.filter(news_shared_date=date_str)

        
        if not queryset.exists():
            return Response({"detail": "No News Articles found."}, status=status.HTTP_404_NOT_FOUND)

        
        data = {
            'Title': [article.title for article in queryset],
            'Content': [article.content for article in queryset],
            'Date': [article.news_shared_date.replace(tzinfo=None) for article in queryset],
            'Source ID': [article.source_id for article in queryset],
        }

        df = pd.DataFrame(data)

        
        excel_filename = f'news_articles_{date_str}.xlsx'
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={excel_filename}'

        
        df.to_excel(response, index=False)

        return response
    
    
    


class MostlySourcesRegionAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token.",
            }, status=status.HTTP_401_UNAUTHORIZED)

        # cached_data = cache.get('mostly_sources_region')
        # if cached_data is None:
        regions = (
            Region.objects
            .annotate(sources_count=Count('sources'))
            .order_by('-sources_count')[:5]
        )

        serializer = MostlySourcesRegionSerializer(regions, many=True)
        # cache.set('mostly_sources_region', serializer.data, timeout=86400)

        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class AllSourceCountAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token.",
            }, status=status.HTTP_401_UNAUTHORIZED)

        total_sources = Source.objects.count()
        total_regions = Region.objects.count()
        total_articles = NewsArticle.objects.count()
        total_telegram_channels = Source.objects.filter(type=2).count()

        if total_articles >= 1_000_000:
            formatted_articles = f"{round(total_articles / 1_000_000, 1)}+"
        elif total_articles >= 100_000:
            formatted_articles = f"{round(total_articles / 1_000_000, 1)}+"
        else:
            formatted_articles = f"{round(total_articles / 1_000_000, 2)}+"

        data = {
            "total_sources": total_sources,
            "total_regions": total_regions,
            "total_articles": formatted_articles,
            "total_telegram_channels": total_telegram_channels
        }


        return Response({
            "status": "success",
            "data": data
        }, status=status.HTTP_200_OK)



# --- 2. DailyArticleCountView ---

#son 21 gunde gundelik meqale sayi
class DailyArticleCountView(APIView):
    serializer_class = DailyArticleCountSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token.",
            }, status=status.HTTP_401_UNAUTHORIZED)

        

        today = timezone.now().date()
        last_21_days = today - timedelta(days=20)

        articles = (
            NewsArticle.objects.filter(created_at__date__gte=last_21_days)
            .values('created_at__date')
            .annotate(article_count=Count('id'))
        )

        results = defaultdict(int)
        for article in articles:
            results[article['created_at__date']] += article['article_count']

        formatted_results = []
        for date, count in sorted(results.items()):
            formatted_results.append({
                "date": self.format_date(date),
                "count": count
            })

        return Response({
            "status": "success",
            "data": formatted_results
        }, status=status.HTTP_200_OK)

    def format_date(self, date):
        months = {
            1: 'Yan', 2: 'Fev', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'İyn',
            7: 'İyl', 8: 'Avq', 9: 'Sen', 10: 'Okt', 11: 'Noy', 12: 'Dek'
        }
        return f"{date.day} {months[date.month]}"



# --- 3. DailyArticleCountryCountView ---

#son 14 gunde olkeler uzre meqale sayi
class WeeklyArticleCountryCountView(APIView):
    serializer_class = DailyArticleCountryCountSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token.",
            }, status=status.HTTP_401_UNAUTHORIZED)

        

        today = timezone.now().date()
        last_14_days = today - timedelta(days=13)

        queryset = (
            NewsArticle.objects
            .filter(news_shared_date__date__gte=last_14_days)
            .values(country_name=F('source__region_id__name'))
            .annotate(count=Count('id'))
        )

        formatted_results = [
            {
                "country": item["country_name"] or "undefined",
                "count": item["count"]
            }
            for item in queryset
        ]

        return Response({
            "status": "success",
            "data": formatted_results
        }, status=status.HTTP_200_OK)





#butun zamanlar ucun olkeler uzre meqale sayi
class AllTimeArticleCountryCountView(APIView):
    serializer_class = DailyArticleCountryCountSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token.",
            }, status=status.HTTP_401_UNAUTHORIZED)

        queryset = (
            NewsArticle.objects
            .values(country_name=F('source__region_id__name'))
            .annotate(count=Count('id'))
        )

        formatted_results = [
            {
                "country": item["country_name"] or "undefined",
                "count": item["count"]
            }
            for item in queryset
        ]
        
        return Response({
            "status": "success",
            "data": formatted_results
        }, status=status.HTTP_200_OK)





class CheckSourceSitesView(APIView):
    
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

    def post(self, request):
        site_link = request.data.get("site_link")

       
        if not site_link:
            sources = Source.objects.all().values(
                "id", "name", "link", "rss_link", "region_id", "type", "created_at","is_active"
            )
            return Response({
                "status": "success",
                "count": sources.count(),
                "results": list(sources)
            }, status=status.HTTP_200_OK)

        try:
            headers  = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
            response = requests.get(site_link, headers=headers, timeout=15)

            if response.status_code == 200:
                return Response({
                    "status": "success",
                    "message": "Site is accessible.",
                    "http_status": response.status_code,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "warning",
                    "message": f"Site access failed. HTTP {response.status_code}",
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "status": "error",
                "message": f"Site access failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    

class UpdateSourceActiveStatus(APIView):
    
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

    def post(self, request):
        site_link = request.data.get("site_link")
        is_active = request.data.get("is_active")


        if site_link is None or is_active is None:
            return Response({
                "status": "error",
                "message": "site_link and is_active parameters are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            source = Source.objects.get(link=site_link)
            source.is_active = bool(is_active)
            source.save(update_fields=["is_active"])

            return Response({
                "status": "success",
                "message": f"{source.name or site_link} source's active status has been updated.",
                "source_id": source.id,
                "is_active": source.is_active
            }, status=status.HTTP_200_OK)

        except Source.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Source not found for this link: {site_link}"
            }, status=status.HTTP_404_NOT_FOUND)




class GetNewsFromFacebook(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data

        if isinstance(data, list):
            results = []
            for item in data:
                results.append(self.process_single_item(item))
            return Response(results, status=status.HTTP_200_OK)

        return Response(self.process_single_item(data), status=status.HTTP_200_OK)

    def process_single_item(self, item):
        from scraper.models import Source, NewsArticle, ChangedNewsArticle, NewsImage
        from utils.photo_save import download_and_resize_image

        source_name = item.get("source_name", "Facebook")
        source_link = item.get("source_link", "www.facebook.com")
        url = item.get("url")
        content = item.get("content", "")
        gallery_images = item.get("gallery", [])
        news_shared_date = item.get("news_shared_date") or timezone.now()

        clean_gallery = [g for g in (gallery_images or []) if g and g.strip()]

        if not url:
            return {"status": "error", "message": "URL is required."}

        source = Source.objects.filter(link=source_link).first()
        if not source:
            return {"status": "error", "message": f"Source '{source_name}' not found.", "url": url}

        existing_article = NewsArticle.objects.filter(url=url).first()

        if existing_article:

            existing_gallery_urls = set(existing_article.images.values_list("image_url", flat=True))
            new_gallery_urls = set(clean_gallery)

            content_changed = existing_article.content != content
            images_changed = existing_gallery_urls != new_gallery_urls

            if content_changed or images_changed:
                changed = ChangedNewsArticle.objects.create(
                    newsarticle=existing_article,
                    title=None,
                    description=None,
                    content=existing_article.content if content_changed else None,
                )

                for img in existing_article.images.all():
                    NewsImage.objects.create(
                        changed_newsarticle=changed,
                        image_url=img.image_url,
                        local_image_url=img.local_image_url,
                        base64_image=img.base64_image,
                        is_main=img.is_main
                    )

                existing_article.content = content
                existing_article.news_shared_date = news_shared_date
                existing_article.save()

                existing_article.images.all().delete()

                for idx, img_url in enumerate(clean_gallery):
                    file_content = download_and_resize_image(img_url, instance=existing_article)
                    NewsImage.objects.create(
                        newsarticle=existing_article,
                        image_url=img_url,
                        local_image_url=file_content,
                        is_main=(idx == 0)
                    )

                return {"status": "updated", "article_id": existing_article.id, "url": url}

            return {"status": "no_change", "article_id": existing_article.id, "url": url}

        article = NewsArticle.objects.create(
            source=source,
            url=url,
            content=content,
            news_shared_date=news_shared_date
        )

        for idx, img_url in enumerate(clean_gallery):
            file_content = download_and_resize_image(img_url, instance=article)
            NewsImage.objects.create(
                newsarticle=article,
                image_url=img_url,
                local_image_url=file_content,
                is_main=(idx == 0)
            )

        return {"status": "created", "article_id": article.id, "url": url}

            
        
            
        
            
        
            
        
        
        
        
