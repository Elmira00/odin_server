from django.urls import path
from .views import KeywordsLastTwoWeekCounts,KeywordsMostPopular,UserMatchedArticlesListAPIView



urlpatterns = [
    path('KeywordsLastTwoWeekCounts/', KeywordsLastTwoWeekCounts.as_view(), name='KeywordsLastTwoWeekCounts'),
    path('KeywordsMostPopular/', KeywordsMostPopular.as_view(), name='KeywordsMostPopular'),
    path('ArticlesMatched/', UserMatchedArticlesListAPIView.as_view(), name='ArticlesMatched'),
]
