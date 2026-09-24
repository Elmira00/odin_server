from django.urls import path
from .views import get_news_links_oxu

urlpatterns = [
    path('get-news-links_oxu', get_news_links_oxu, name='get_news_links_oxu'),
]