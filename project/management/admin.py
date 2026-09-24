from django.contrib import admin
from .models import *


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_filter = ('source__region_id', 'category') 
    autocomplete_fields = ('source',)
    search_fields = ('problem_description', 'source__name')

    fields = (  
        'source',
        'category',
        'is_sent',
        'problem_description',
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    autocomplete_fields = ('problem',)
    search_fields = ('content', 'created_by__username', 'assigned_to__username')
    readonly_fields=('get_category',)
    inlines=[CommentInline]
    fields = (
        'problem',            
        'get_category',  
        'category',   
        'created_by',
        'status',
        'assigned_to',
        'content',           
        'is_deleted' 
    )
    def get_category(self, obj):
        return obj.effective_category
    get_category.short_description = 'Category'

    list_display = ('display_str','is_deleted')

    def display_str(self, obj):
        return str(obj) 


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'description')
    autocomplete_fields = ('user', 'task')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category',)

# @admin.register(SourceRule)
# class SourceRuleAdmin(admin.ModelAdmin):
#     list_display = ('problem', 'resolution_type', 'rule_content', 'is_active')
#     list_filter = ('is_active', 'resolution_type')
#     search_fields = ('rule_content', 'problem__source__name', 'problem__problem_description')
#     autocomplete_fields = ('problem',)


import json
from django.utils.html import format_html

@admin.register(SourceRule)
class SourceRuleAdmin(admin.ModelAdmin):
    list_display = ('problem', 'resolution_type', 'rule_content', 'is_active', 'view_tested_urls')
    # list_filter = ('is_active', 'resolution_type')
    search_fields = ('rule_content', 'problem__source__name', 'problem__problem_description')
    autocomplete_fields = ('problem',)
    
    readonly_fields = ('view_tested_urls',)
    fields = ('problem', 'resolution_type', 'rule_content', 'is_active', 'view_tested_urls')

    def view_tested_urls(self, obj):
        if not obj.problem or not obj.problem.problem_description:
            return "-"
        
        try:
            desc = obj.problem.problem_description
            
            if isinstance(desc, str):
                problem_desc = json.loads(desc)
            elif isinstance(desc, dict):
                problem_desc = desc
            else:
                return "Yanlış format"
            
            if not isinstance(problem_desc, dict):
                return "-"
            
            articles = problem_desc.get("articles", [])
            urls = []
            
            for article in articles:
                if isinstance(article, dict):
                    url = article.get("url")
                    if url:
                        urls.append(url)
                elif isinstance(article, str): 
                    urls.append(article)
            
            urls = urls[:5]
            
            if not urls:
                return "URL tapılmadı"
            
            links = [f'<a href="{url}" target="_blank">{url}</a>' for url in urls]
            return format_html("<br><br>".join(links)) 
            
        except Exception as e:
            return f"Xəta: {str(e)}"  



@admin.register(AutoHealerFinding)
class AutoHealerFindingAdmin(admin.ModelAdmin):
    list_display = ('source', 'category', 'status', 'resolution_type', 'confidence', 'created_at')
    list_filter = ('status', 'resolution_type', 'category')
    search_fields = ('rule_content', 'source__name')
    autocomplete_fields = ('source', 'category')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')