from django.urls import path
from .views import RegionListApiView,NewsArticleListApiView,\
NewsArticleDetailAPIView,ExportNewsArticlesView,\
    MostlySourcesRegionAPIView,AllSourceCountAPIView,DailyArticleCountView,AllTimeArticleCountryCountView,\
        WeeklyArticleCountryCountView,CheckSourceSitesView,UpdateSourceActiveStatus,GetNewsFromFacebook,NewsArticleSearchApiView
   


urlpatterns = [
    path('SourcesByRegion/', RegionListApiView.as_view(), name='SourcesByRegion'), 
    path('Article/', NewsArticleDetailAPIView.as_view(), name='Article'),
    path('ArticlesAll/', NewsArticleListApiView.as_view(), name='ArticlesAll'),

    path('ArticleSearch/', NewsArticleSearchApiView.as_view(), name='ArticleSearch'),

    path('export-news-articles/', ExportNewsArticlesView.as_view(), name='export-news-articles'),

    #yenilenmis urls
    path('SourcesCountByRegionTopFive/',MostlySourcesRegionAPIView.as_view(), name='SourcesCountByRegionTopFive'),
    
    path('TotalCounts/', AllSourceCountAPIView.as_view(), name='TotalCounts'),
    
    path('ArticleCountsLastThreeWeeks/', DailyArticleCountView.as_view(), name='ArticleCountsLastThreeWeeks'),
    
    path('ArticleCountsByRegionLastWeeks/', WeeklyArticleCountryCountView.as_view(), name='ArticleCountsByRegionLastWeeks'),
    path('ArticleCountsByRegion/', AllTimeArticleCountryCountView.as_view(), name='ArticleCountsByRegion'),
    
    
    path('check-source-sites/', CheckSourceSitesView.as_view(), name='check-source-sites'),
    path('update-source-active-status/', UpdateSourceActiveStatus.as_view(), name='update-source-active-status'),
    path('get-news-from-facebook/', GetNewsFromFacebook.as_view(), name='get-news-from-facebook'),
]

