import json
import subprocess

from management.models import *
from rest_framework.generics import *
from management.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from management.api.pagination import TaskPagination,ProblemPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import *
from django.views.decorators.cache import cache_page
from scraper.models import *
from user.authentication import CustomTokenAuthentication
from management.api.permissions import CanArchiveTask
# from drf_spectacular.utils import OpenApiParameter, extend_schema
# from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from management.api.filters import ProblemFilter

# @extend_schema(
#     summary="Assign yourself to a task",
#     description="Assigns the authenticated user to the task with the given ID.",
#     parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH, description="Task ID"),
#                 OpenApiParameter(name='X-User-Id', type=OpenApiTypes.INT, location=OpenApiParameter.HEADER),
#                 OpenApiParameter(name='X-Expire-Date', type=OpenApiTypes.DATETIME, location=OpenApiParameter.HEADER),
#                 OpenApiParameter(name='X-Auth-Token', type=OpenApiTypes.STR, location=OpenApiParameter.HEADER),],
  
#     tags=["Tasks"]
# )
class AssignMeView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, is_deleted=False)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        task.assigned_to.add(request.user)
        return Response({"detail": "You have been assigned to this task."}, status=status.HTTP_200_OK)


# @extend_schema(
#     summary="List and create tasks",
#     description="Returns a list of tasks. Also allows creation of new tasks.",
#     parameters=[
#         OpenApiParameter(name='X-User-Id', type=OpenApiTypes.INT, location=OpenApiParameter.HEADER),
#         OpenApiParameter(name='X-Expire-Date', type=OpenApiTypes.DATETIME, location=OpenApiParameter.HEADER),
#         OpenApiParameter(name='X-Auth-Token', type=OpenApiTypes.STR, location=OpenApiParameter.HEADER),
#     ],
#     tags=["Tasks"]
# )
class TaskList(ListCreateAPIView):
    queryset = Task.objects.filter(is_deleted=False).exclude(status='archived')
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.assigned_to.set([self.request.user])
        
class ArchivedTaskList(ListAPIView):
    queryset = Task.objects.filter(is_deleted=False, status='archived')
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenAuthentication]
    
class ArchivedTaskDetail(RetrieveAPIView):
    queryset = Task.objects.filter(is_deleted=False, status='archived')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]
    

# @extend_schema(
#     summary="Retrieve, update or delete a task",
#     description="Retrieve, update, or soft-delete a task by ID.",
#     parameters=[
#         OpenApiParameter(name='X-User-Id', type=OpenApiTypes.INT, location=OpenApiParameter.HEADER),
#         OpenApiParameter(name='X-Expire-Date', type=OpenApiTypes.DATETIME, location=OpenApiParameter.HEADER),
#         OpenApiParameter(name='X-Auth-Token', type=OpenApiTypes.STR, location=OpenApiParameter.HEADER),
#     ],
#     tags=["Tasks"]
# )
class TaskDetail(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.filter(is_deleted=False).exclude(status='archived')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, CanArchiveTask] 
    authentication_classes=[CustomTokenAuthentication]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"detail": "task deleted"}, status=status.HTTP_200_OK)
    def perform_update(self, serializer):
        instance = self.get_object()
        old_status = instance.status
        new_status = self.request.data.get("status", old_status)
        comment_text = self.request.data.get("comment", "").strip()

        if new_status != old_status and not comment_text:
            raise ValidationError("A comment is required when changing the task status.")

        serializer.save()

        if comment_text:
            Comment.objects.create(
                user=self.request.user,
                task=instance,
                comment=comment_text
            )


# @extend_schema(tags=["Categories"])
class CategoryList(ListCreateAPIView):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]


# @extend_schema(tags=["Categories"])
class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"detail": "Category deleted"}, status=status.HTTP_200_OK)

# @extend_schema(tags=["Problems"])
class ProblemList(ListAPIView):
    queryset = Problem.objects.filter(is_deleted=False)
    serializer_class = ProblemSerializer
    #permission_classes=[IsAuthenticated]
    pagination_class = ProblemPagination
    #authentication_classes=[CustomTokenAuthentication]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProblemFilter
    ordering_fields = ['created_at', 'id']
    ordering = ['-created_at'] 

# @extend_schema(tags=["Problems"])
class ProblemDetail(RetrieveDestroyAPIView):
    queryset = Problem.objects.filter(is_deleted=False)
    serializer_class = ProblemSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"detail": "Problem deleted"}, status=status.HTTP_200_OK)


# @extend_schema(tags=["Comments"])
class CommentList(ListCreateAPIView):
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]


# @extend_schema(tags=["Comments"])
class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"detail": "Comment deleted"}, status=status.HTTP_200_OK)



# Statistics Views

# @extend_schema(
#     summary="Most problematic category",
#     description="Returns the category with the highest number of problems.",
#     tags=["Statistics"]
# )
@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
@cache_page(60 * 60 * 12) 
def most_problematic_categories(request):
    
    data = (
        Problem.objects.filter(is_deleted=False, category__is_deleted=False)
        .values('category__category')
        .annotate(problem_count=Count('id'))
        .order_by('-problem_count')[:7]
    )
    
    result = [
        {
            "category": item["category__category"],
            "problem_count": item["problem_count"]
        }
        for item in data
    ]

    return Response(result)




# @extend_schema(
#     summary="Top 7 sources by problem count",
#     description="Returns the top 7 sources with the most problems reported.",
#     tags=["Statistics"]
# )
@api_view(['GET'])
# @authentication_classes([CustomTokenAuthentication])
# @permission_classes([IsAuthenticated])
@cache_page(60 * 60 * 12)
def top_problem_sources(request):
    data = (
        Problem.objects.values('source__name')
        .annotate(problem_count=Count('id'))
        .order_by('-problem_count')[:7]
    )
    return Response(data)


# @extend_schema(
#     summary="Problem count by region",
#     description="Returns the count of problems grouped by region.",
#     tags=["Statistics"]
# )
@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
@cache_page(60 * 60 * 12)
def problems_by_region(request):
    data = (
        Problem.objects.filter(source__region_id__isnull=False)
        .values('source__region_id__name')
        .annotate(problem_count=Count('id'))
        .order_by('-problem_count')
    )
    return Response(data)


# @extend_schema(
#     summary="14-day problem/task statistics",
#     description="Returns the number of problems, created tasks, and completed tasks in the last 14 days.",
#     tags=["Statistics"]
# )
@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
@cache_page(60 * 60 * 12)
def task_stats_14_days(request):
    now = timezone.now()
    start_date = now - timedelta(days=14)

    problems_count = Problem.objects.filter(created_at__gte=start_date).count()
    tasks_created = Task.objects.filter(created_at__gte=start_date).count()
    tasks_completed = Task.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).count()

    return Response({
        'problems_last_14_days': problems_count,
        'tasks_created_last_14_days': tasks_created,
        'tasks_completed_last_14_days': tasks_completed,
    })


# @extend_schema(
#     summary="Top 7 changed sources",
#     description="Returns the top 7 sources with the most changed news articles.",
#     tags=["Statistics"]
# )
@api_view(['GET'])
# @authentication_classes([CustomTokenAuthentication])
# @permission_classes([IsAuthenticated])
@cache_page(60 * 60 * 12)
def most_changed_sources(request):
    data = (
        Source.objects
        .annotate(change_count=Count('newsarticles__changednewsarticles'))
        .order_by('-change_count')[:7]
        .values('name', 'change_count')
    )
    return Response(data)



class CheckLastNewsArticleDateforSourceView(APIView):
    
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

    def post(self, request):
        site_link = request.data.get("site_link")

        # ## sondaki slashi yoxlamaq ucun, sondaki /'i silirik
        clean_link = site_link.rstrip('/')
        source = Source.objects.filter(
            Q(link=clean_link) | Q(link=clean_link + '/')
        ).first()
       
        if not site_link:
            sources = Source.objects.all().values(
                "id", "name", "link", "rss_link", "region_id", "type", "created_at","is_active"
            )
            return Response({
                "status": "success",
                "count": sources.count(),
                "results": list(sources)
            }, status=status.HTTP_200_OK)
            
        if site_link:
            
            try:
                source = Source.objects.get(link=site_link)
            except Source.DoesNotExist:
                return Response({"detail": "Source not found."}, status=status.HTTP_404_NOT_FOUND)

            last_article = NewsArticle.objects.filter(source=source).order_by('-created_at').first()

            if last_article:
                return Response({
                    "status": "success",
                    "last_article_date": last_article.created_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No articles found for this source."}, status=status.HTTP_404_NOT_FOUND)

        
from django.db import connection
from management.tasks import r


class StatisticsAPIView(APIView):
    def get(self, request):
        cached_data = r.get("stats:general_dashboard")
        if cached_data:
            return Response(json.loads(cached_data), status=status.HTTP_200_OK)

        today = timezone.now().date()

        total_articles = NewsArticle.objects.count()
        total_sources = Source.objects.count()
        total_telegram_channels = Source.objects.filter(type=2).count()
        total_websites = total_sources - total_telegram_channels

        sources_breakdown = Region.objects.annotate(
            total_sources=Count("sources"),
            telegram=Count("sources", filter=Q(sources__type=2)),
        ).annotate(
            websites=F("total_sources") - F("telegram")
        ).values("name", "total_sources", "websites", "telegram")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_size_pretty(pg_database_size(current_database()));"
            )
            db_size_pretty = cursor.fetchone()[0]

        disk_stats = {"server": {}, "images": {}}
        try:
            df_output = subprocess.check_output(["df", "-h"]).decode("utf-8")
            lines = df_output.strip().split("\n")[1:]

            for line in lines:
                parts = line.split()
                if len(parts) < 6:
                    continue

                mount_point = parts[5]
                data = {
                    "filesystem": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "avail": parts[3],
                    "use_percent": parts[4],
                }

                if mount_point == "/":
                    disk_stats["server"] = data
                elif mount_point == "/home/rv/odin/project/media":
                    disk_stats["images"] = data
        except Exception as e:
            disk_stats["error"] = str(e)

        response_data = {
            "date": str(today),
            "total_articles": total_articles,
            "total_websites": total_websites,
            "total_telegram_channels": total_telegram_channels,
            "regions": list(sources_breakdown),
            "storage": disk_stats,
            "database_size": db_size_pretty,
        }

        r.set("stats:general_dashboard", json.dumps(response_data), ex=60 * 60 * 6)

        return Response(response_data, status=status.HTTP_200_OK)


class StatisticsExcelAPIView(APIView):
    def get(self, request):
        cached_data = r.get("stats:excel_json")
        if cached_data:
            return Response(json.loads(cached_data), status=status.HTTP_200_OK)

        today = timezone.now().date()
        current_total = NewsArticle.objects.count()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_size_pretty(pg_database_size(current_database()));"
            )
            db_size = cursor.fetchone()[0]

        last_snapshot_str = r.get("stats:last_snapshot")

        if last_snapshot_str:
            last_snapshot = json.loads(last_snapshot_str)
            last_total = last_snapshot.get("total_articles", current_total)
            last_checked_date = last_snapshot.get("checked_date")
        else:
            last_total = current_total
            last_checked_date = None

        new_articles = max(0, current_total - last_total)

        stats_data = {
            "date": str(today),
            "db_size": db_size,
            "total_articles": current_total,
            "new_articles_since_last_check": new_articles,
            "previous_checked_date": last_checked_date,
        }

        r.set("stats:excel_json", json.dumps(stats_data), ex=60 * 60 * 3)

        r.set(
            "stats:last_snapshot",
            json.dumps({
                "total_articles": current_total,
                "checked_date": str(today),
            }),
            ex=60 * 60 * 24 * 7
        )

        return Response(stats_data, status=status.HTTP_200_OK)



from management.auto_healer.services import run_discovery_diagnostics

class AutoHealerDiagnosticView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenAuthentication]

    def post(self, request):
        urls = request.data.get("urls", [])
        if not urls or not isinstance(urls, list):
            raise ValidationError("A list of 'urls' is required.")
        
        results = run_discovery_diagnostics(urls)
        return Response({
            "status": "success",
            "results": results
        }, status=status.HTTP_200_OK)



import json
from rest_framework.views import APIView
from rest_framework.response import Response
from management.models import AutoHealerFinding
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from management.models import SourceRule, Problem
class PendingFindingsAPIView(APIView):
    """
    Retrieves all PENDING Auto Healer findings for human review.
    """
    def get(self, request):
        # Fetch only PENDING findings, newest first
        findings = AutoHealerFinding.objects.filter(
            status='PENDING'
        ).select_related('source', 'category').order_by('-created_at')
        
        data = []
        for f in findings:
            # Safely parse the rule content back into a dictionary if it's JSON
            try:
                rule = json.loads(f.rule_content)
            except (json.JSONDecodeError, TypeError):
                rule = f.rule_content
            
            # Safely parse evidence URLs
            try:
                urls = json.loads(f.evidence_urls) if f.evidence_urls else []
            except (json.JSONDecodeError, TypeError):
                urls = []

            data.append({
                "id": f.id,
                "source_name": f.source.name if f.source else "Unknown",
                "category_name": f.category.category if f.category else "Unknown",
                "resolution_type": f.resolution_type,
                "rule": rule,
                "confidence": f.confidence,
                "sample_urls": urls,
                "created_at": f.created_at.isoformat()
            })
            
        return Response({"results": data})




class ApproveFindingAPIView(APIView):
    """
    Approves a PENDING finding. Safely deactivates old rules and creates a new SourceRule.
    """
    def post(self, request, pk):
        finding = get_object_or_404(AutoHealerFinding, pk=pk)
        
        if finding.status != 'PENDING':
            return Response(
                {"error": "Only pending findings can be approved."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            # 1. Deactivate existing active rules for this source + category
            SourceRule.objects.select_for_update().filter(
                problem__source=finding.source,
                problem__category=finding.category,
                is_active=True
            ).update(is_active=False)
            
            # 2. Get a reference problem to attach the SourceRule to 
            # (Matches how tasks.py originally assigned target_problem)
            target_problem = Problem.objects.filter(
                source=finding.source, 
                category=finding.category
            ).first()
            
            # 3. Create the new active SourceRule
            SourceRule.objects.create(
                problem=target_problem,
                resolution_type=finding.resolution_type,
                rule_content=finding.rule_content,
                is_active=True
            )
            
            # 4. Mark finding as APPROVED
            finding.status = 'APPROVED'
            finding.reviewed_at = timezone.now()
            finding.save(update_fields=['status', 'reviewed_at'])
            
        return Response({"success": True, "message": "Finding approved and rule is now active."})


class DeclineFindingAPIView(APIView):
    """
    Declines a PENDING finding so it doesn't get suggested again.
    """
    def post(self, request, pk):
        finding = get_object_or_404(AutoHealerFinding, pk=pk)
        
        if finding.status != 'PENDING':
            return Response(
                {"error": "Only pending findings can be declined."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        finding.status = 'DECLINED'
        finding.reviewed_at = timezone.now()
        finding.save(update_fields=['status', 'reviewed_at'])
        
        return Response({"success": True, "message": "Finding declined successfully."})