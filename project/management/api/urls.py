#odin2/project/management/api/urls.py
from django.urls import path
from management.api.views import *

urlpatterns = [
    path('tasks/', TaskList.as_view(), name='task-list'),
    path('tasks/archived/', ArchivedTaskList.as_view(), name='archived-tasks'),
    path('tasks/archived/<int:pk>', ArchivedTaskDetail.as_view(), name='archived-tasks'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tasks/<int:pk>/assign_me/', AssignMeView.as_view(), name='assign-me'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('problems/', ProblemList.as_view(), name='problem-list'),
    path('problems/<int:pk>/', ProblemDetail.as_view(), name='problem-detail'),
    path('comments/', CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    path('most-problematic-category/', most_problematic_categories),
    path('top-problem-sources/', top_problem_sources),
    path('problems-by-region/', problems_by_region),
    path('task-stats-14-days/', task_stats_14_days),
    path('most-changed-sources/', most_changed_sources),
    path('check-last-news-article-date/', CheckLastNewsArticleDateforSourceView.as_view(), name='check-last-news-article-date'),
    path("statistics/", StatisticsAPIView.as_view(), name="statistics"),
    path("statistics/excel/", StatisticsExcelAPIView.as_view(), name="statistics-excel"),
    path('auto-healer/diagnostics/', AutoHealerDiagnosticView.as_view(), name='auto-healer-diagnostics'),
    path('auto-healer/findings/pending/', PendingFindingsAPIView.as_view(), name='pending-findings'),
    path('auto-healer/findings/<int:pk>/approve/', ApproveFindingAPIView.as_view(), name='approve-finding'),
    path('auto-healer/findings/<int:pk>/decline/', DeclineFindingAPIView.as_view(), name='decline-finding'),
]
