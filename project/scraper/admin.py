from django.contrib import admin
from .models import *
from django.http import HttpResponse
import pandas as pd
from .forms import ExportNewsArticlesForm
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from datetime import datetime
import pytz


class ChangedNewsArticleInline(admin.TabularInline):
    model = ChangedNewsArticle
    readonly_fields = ('newsarticle',)  
    extra = 0
    raw_id_fields = ('newsarticle',)   


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    readonly_fields = ('newsarticle', 'changed_newsarticle', 'image_url', 'base64_image', 'is_main')
    extra = 0
    raw_id_fields = ('newsarticle', 'changed_newsarticle')


class NewsArticleAdmin(admin.ModelAdmin):
    inlines = [ChangedNewsArticleInline, NewsImageInline]
    list_display = ('id', 'url','source__name', 'title','news_shared_date', 'created_at')
    search_fields = ('title', 'content','source__name')
    list_filter = ('source','source__region_id','news_shared_date')   
    
    change_list_template = "admin/newsarticle_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-news-articles/', self.admin_site.admin_view(self.export_news_articles), name='export_news_articles'),
        ]
        return custom_urls + urls

    def export_news_articles(self, request):
        if request.method == "POST":
            form = ExportNewsArticlesForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                tz = pytz.timezone('Asia/Baku')
                
                
                datetime_with_tz = tz.localize(datetime.combine(date, datetime.min.time()))
                
                
                articles = NewsArticle.objects.filter(news_shared_date__date=datetime_with_tz.date())

                
                data = []
                for article in articles:
                    
                    naive_date = article.news_shared_date.replace(tzinfo=None)
                    data.append({
                        'ID': article.id,
                        'URL': article.url,
                        'Title': article.title,
                        'Content': article.content,
                        'Created At': naive_date,
                    })

                df = pd.DataFrame(data)

                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename=articles_{date}.xlsx'

                
                df.to_excel(response, index=False)
                
                articles.delete()

                return response
        else:
            form = ExportNewsArticlesForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, "admin/export_news_articles.html", context)

    
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_at')
    
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'region_id', 'created_at', 'is_active')
    search_fields = ('name', 'id', 'link')
    list_filter = ('region_id','is_active')
    ordering = ('id',)
    
    
class SearchWordsAdmin(admin.ModelAdmin): 
    list_display = ('id','word', 'created_at')


@admin.register(Exclude)
class ExcludeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('source',)


admin.site.register(Region, RegionAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(SearchWords, SearchWordsAdmin)
admin.site.register(NewsImage)
admin.site.register(ChangedNewsArticle)
