
import django_filters
from django.db import models
from scraper.models import NewsArticle,SearchWords




class NewsArticleFilter(django_filters.FilterSet):
    news_shared_date = django_filters.DateFromToRangeFilter()  
    search = django_filters.CharFilter(method='filter_by_keyword') 
    source = django_filters.NumberFilter(field_name='source_id')
    class Meta:
        model = NewsArticle
        fields = ['news_shared_date', 'search','source']

    
    def filter_by_keyword(self, queryset, name, value):
        
        
        return queryset.filter(
            
            models.Q(title__icontains=value) | models.Q(content__icontains=value)
        )