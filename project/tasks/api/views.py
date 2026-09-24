
from rest_framework import generics
from rest_framework.views import APIView
from tasks.models import KeywordsNewsArticleCombination
from django.db.models.functions import TruncDate
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q,Count
from django.utils import timezone
from datetime import timedelta,datetime
import hashlib
import re
from .pagination import UserMatchedArticlePagination
from scraper.models import NewsArticle
from collections import defaultdict
from django.contrib.postgres.aggregates import ArrayAgg


# def clean_keyword(keyword):
    
#     cleaned = re.sub(r'[^\p{L}\s]', '', keyword, flags=re.UNICODE)
    

#     cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()


#     letters_only = re.sub(r'[^\\p{L}]', '', cleaned, flags=re.UNICODE)

#     if len(letters_only) < 3:
#         return None  

#     return cleaned


def generate_expected_token(salt="token"):
    current_time = datetime.now().strftime("%Y%m%d %H")

    inner_hash = hashlib.md5(current_time.encode()).hexdigest()

    final_hash = hashlib.md5((salt + inner_hash).encode()).hexdigest()

    return final_hash




class KeywordsLastTwoWeekCounts(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        token = request.data.get("token")
        keywords = request.data.get("keywords")

        if not user_id or not token:
            return Response({
                "status": "error",
                "message": "user_id and token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        cache_key = f"last_two_week_counts_{user_id}"
        result = cache.get(cache_key)

        if result is None:
            today = timezone.now().date()
            start_date = today - timedelta(days=14)

            queryset = (
                KeywordsNewsArticleCombination.objects
                .filter(
                    user_id=user_id,
                    keyword_id__in=keywords,
                    created_at__gte=start_date
                )
                .values("keyword_id")
                .annotate(total=Count("id"))
            )

            result = {str(item["keyword_id"]): item["total"] for item in queryset}

            for kw in keywords:
                result.setdefault(str(kw), 0)

            cache.set(cache_key, result, timeout=10800) 

        return Response({
            "status": "success",
            "data": result
        }, status=status.HTTP_200_OK)


class KeywordsMostPopular(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        token = request.data.get("token")
        keywords = request.data.get("keywords")

        if not user_id or not token:
            return Response({
                "status": "error",
                "message": "user_id and token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()
        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not keywords or not isinstance(keywords, list):
            return Response({"status": "error", "message": "keywords must be list"}, status=400)

        cache_key = f"most_popular_{user_id}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        today = timezone.now()
        start_10_days = today - timedelta(days=10)

        top_keywords = (
            KeywordsNewsArticleCombination.objects
            .filter(user_id=user_id, keyword_id__in=keywords)
            .values("keyword_id")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        top_keyword_ids = [k["keyword_id"] for k in top_keywords]

        if not top_keyword_ids:
            response = {"status": "success", "data": {}}
            cache.set(cache_key, response, timeout=10800)
            return Response(response)

        daily_counts = (
            KeywordsNewsArticleCombination.objects
            .filter(
                user_id=user_id,
                keyword_id__in=top_keyword_ids,
                created_at__gte=start_10_days
            )
            .annotate(day=TruncDate("created_at"))
            .values("day", "keyword_id")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        result = {}
        for item in daily_counts:
            day = item["day"].strftime("%d.%m.%Y")
            keyword = str(item["keyword_id"])
            count = item["count"]

            if day not in result:
                result[day] = {}

            result[day][keyword] = count

        response = {
            "status": "success",
            "top_keywords": top_keyword_ids,
            "data": result
        }

        cache.set(cache_key, response, timeout=10800)

        return Response(response)
    
    
    
    
class UserMatchedArticlesListAPIView(APIView):

    pagination_class = UserMatchedArticlePagination

    def post(self, request, *args, **kwargs):

        user_id = request.data.get("user_id")
        token = request.data.get("token")

        search = request.data.get("search")
        publish_date_start = request.data.get("publish_date_start")
        source_id = request.data.get("source_id")
        region_id = request.data.get("region_id")

        if not user_id or not token:
            return Response({
                "status": "error",
                "message": "user_id and token are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        expected_token = generate_expected_token()

        if token != expected_token:
            return Response({
                "status": "error",
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # MAIN QUERY (optimized)
        articles = (
            NewsArticle.objects
            .filter(newsarticle_keywords__user_id=user_id)
            .select_related("source")
            .annotate(
                matched_keywords=ArrayAgg(
                    "newsarticle_keywords__keyword_id",
                    filter=Q(newsarticle_keywords__user_id=user_id),
                    distinct=True
                )
            )
            .distinct()
            .order_by("-created_at")
        )

        # SEARCH
        if search:
            articles = articles.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(content__icontains=search)
            )

        # DATE
        if publish_date_start:
            articles = articles.filter(
                news_shared_date__gte=publish_date_start
            )

        # SOURCE
        if source_id:
            articles = articles.filter(source_id=source_id)

        # REGION
        if region_id:
            articles = articles.filter(source__region_id=region_id)

        paginator = self.pagination_class()

        paginated_articles = paginator.paginate_queryset(
            articles, request
        )

        data = []

        for article in paginated_articles:

            data.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source.name if article.source else None,
                "source_id": article.source.id if article.source else None,
                "region_id": (
                    article.source.region_id.id
                    if article.source and article.source.region_id
                    else None
                ),
                "created_at": article.created_at,
                "updated_at": article.updated_at,
                "matched_keywords": article.matched_keywords or []
            })

        return paginator.get_paginated_response(data)
