from rest_framework import serializers
# from django.core.validators import MinValueValidator, MaxValueValidator
from scraper.models import NewsArticle, ChangedNewsArticle, Source, Region
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.db.models import Count



class ChangedNewsArticleSerializerForNewsArticle(serializers.ModelSerializer):
    
    class Meta:
        model = ChangedNewsArticle
        fields = ('id','title','description','content', 'created_at')
        
        
class RegionSerializerForSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class SourceSerializerForNewsArticleSerializer(serializers.ModelSerializer):
    
    region = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = ('id', 'name', 'region')

    def get_region(self, obj):
        if obj.region_id:
            return {
                "id": obj.region_id.id,
                "name": obj.region_id.name
            }
        return None
        
        
        
class NewsArticleAccessSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, write_only=True)
    search = serializers.CharField(required=False, allow_blank=True)
    
    publish_date_start = serializers.DateField(required=False, allow_null=True)
    publish_date_end = serializers.DateField(required=False, allow_null=True)
    
    source_id = serializers.IntegerField(required=False, allow_null=True)
    region_id = serializers.IntegerField(required=False, allow_null=True)
    page = serializers.IntegerField(required=False, default=1)
    
    



class NewsArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializerForNewsArticleSerializer(read_only=True)
    news_shared_date = serializers.DateTimeField()  
    class Meta:
        model = NewsArticle
        fields = (
            'id',
            'url',
            'title',
            'description',
            'news_shared_date',
            'created_at',
            'updated_at',
            'source',
        )


class NewsArticleDetailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, write_only=True)
    id = serializers.IntegerField(required=True)
    
    
    
class ChangedNewsArticleHistorySerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()
    image_url = serializers.URLField()
    created_at = serializers.DateTimeField()

    

    


class SourceSerializer(serializers.ModelSerializer):
    newsarticles = NewsArticleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Source
        fields = '__all__'
        




class SourceSerializerForRegion(serializers.ModelSerializer):    
    class Meta:
        model = Source
        fields = ('id', 'name')


class RegionSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)





class NewsArticleMonthlySerializer(serializers.Serializer):
    month = serializers.SerializerMethodField()
    article_count = serializers.IntegerField()

    def get_month(self, obj):
        return obj['month'].strftime('%Y-%m')

    @staticmethod
    def get_monthly_article_count():
        articles_per_month = (NewsArticle.objects.annotate(month=TruncMonth('created_at'))
            .values('month').annotate(article_count=Count('id')).order_by('month')
        )
        return articles_per_month
    
    


class NewsArticleCountbyRegionSerializer(serializers.Serializer):
    region = serializers.CharField(source='name')
    article_count = serializers.IntegerField()





class MostlySourcesRegionSerializer(serializers.ModelSerializer):
    sources_count = serializers.SerializerMethodField()
    sources_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['name', 'sources_count', 'sources_percentage']

    def get_sources_count(self, obj):
        return obj.sources_count

    def get_sources_percentage(self, obj):
        total_sources = Source.objects.count()
        return round((obj.sources_count / total_sources) * 100, 2) if total_sources > 0 else 0.0
    


class MostlyArticlesSourceSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = ['name', 'articles_count']

    def get_articles_count(self, obj):
        return obj.newsarticles.count() 

    
class AllSourceCountSerializer(serializers.Serializer):
    all_sources_count = serializers.IntegerField()
    
    
    
    
    
#--------------------For DailyArticleCountView -------------------
    

class DailyArticleCountSerializer(serializers.Serializer):
    date = serializers.CharField()
    count = serializers.IntegerField()
    
#---------------------------------------------------------------
    
class DailyArticleCountryCountSerializer(serializers.Serializer):
    country = serializers.CharField()
    count = serializers.IntegerField()
    
    
    
