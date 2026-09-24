import json
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from celery import shared_task
from .resolvers import (
    ImageAutoHealer, 
    TitleAutoHealer, 
    ContentAutoHealer, 
    DescriptionAutoHealer,
    SharedDateAutoHealer
)
from management.models import Problem, SourceRule


@shared_task
def trigger_image_auto_healing():
    category_name = "empty image"
    time_threshold = timezone.now() - timedelta(minutes=30) ################
    problems = Problem.objects.filter(
        category__category=category_name, 
        is_deleted=False,
        created_at__gte=time_threshold
    )
    
    for problem in problems:
        source_id = problem.source_id
        cache_key = f"healer_processed_{source_id}_{category_name}"
        
        if cache.get(cache_key):
            continue

        if not problem.problem_description:
            continue
            
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            continue

        articles = problem_desc.get("articles", [])
        urls_to_test = [article.get("url") for article in articles if article.get("url")][:5]

        if urls_to_test:
            healer = ImageAutoHealer(source_id=source_id, test_urls=urls_to_test)
            result = healer.run_diagnostics()
            
            if result and isinstance(result, dict):
                resolution_type = result.get("resolution_type")
                rule_content = result.get("rule")
                
                if resolution_type and rule_content:
                    SourceRule.objects.filter(
                        problem__source_id=source_id, 
                        problem__category__category=category_name,
                        is_active=True
                    ).update(is_active=False)
                    
                    SourceRule.objects.create(
                        problem=problem,
                        resolution_type=resolution_type,
                        rule_content=rule_content,
                        is_active=True
                    )
                    print(f"{rule_content} qaydası ilə {resolution_type} həll edildi.")
            
            cache.set(cache_key, True, timeout=3600)
            
    return "Image healing tamamlandı."


@shared_task
def trigger_title_auto_healing():
    category_name = "empty title"
    time_threshold = timezone.now() - timedelta(minutes=30)
    problems = Problem.objects.filter(
        category__category=category_name, 
        is_deleted=False,
        created_at__gte=time_threshold
    )
    
    for problem in problems:
        source_id = problem.source_id
        cache_key = f"healer_processed_{source_id}_{category_name}"
        
        if cache.get(cache_key):
            continue

        if not problem.problem_description:
            continue
            
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            continue

        articles = problem_desc.get("articles", [])
        urls_to_test = [article.get("url") for article in articles if article.get("url")][:5]

        if urls_to_test:
            healer = TitleAutoHealer(source_id=source_id, test_urls=urls_to_test)
            result = healer.run_diagnostics()
            
            if result and isinstance(result, dict):
                resolution_type = result.get("resolution_type")
                rule_content = result.get("rule")
                
                if resolution_type and rule_content:
                    SourceRule.objects.filter(
                        problem__source_id=source_id, 
                        problem__category__category=category_name,
                        is_active=True
                    ).update(is_active=False)
                    
                    SourceRule.objects.create(
                        problem=problem,
                        resolution_type=resolution_type,
                        rule_content=rule_content,
                        is_active=True
                    )
                    print(f"{rule_content} qaydası ilə {resolution_type} həll edildi.")
            
            cache.set(cache_key, True, timeout=3600)
            
    return "Title healing tamamlandı."


@shared_task
def trigger_content_auto_healing():
    category_name = "empty content"
    time_threshold = timezone.now() - timedelta(minutes=30)
    problems = Problem.objects.filter(
        category__category=category_name, 
        is_deleted=False,
        created_at__gte=time_threshold
    )
    
    for problem in problems:
        source_id = problem.source_id
        cache_key = f"healer_processed_{source_id}_{category_name}"
        
        if cache.get(cache_key):
            continue

        if not problem.problem_description:
            continue
            
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            continue

        articles = problem_desc.get("articles", [])
        urls_to_test = [article.get("url") for article in articles if article.get("url")][:5]

        if urls_to_test:
            healer = ContentAutoHealer(source_id=source_id, test_urls=urls_to_test)
            result = healer.run_diagnostics()
            
            if result and isinstance(result, dict):
                resolution_type = result.get("resolution_type")
                rule_content = result.get("rule")
                
                if resolution_type and rule_content:
                    SourceRule.objects.filter(
                        problem__source_id=source_id, 
                        problem__category__category=category_name,
                        is_active=True
                    ).update(is_active=False)
                    
                    SourceRule.objects.create(
                        problem=problem,
                        resolution_type=resolution_type,
                        rule_content=rule_content,
                        is_active=True
                    )
                    print(f"{rule_content} qaydası ilə {resolution_type} həll edildi.")
            
            cache.set(cache_key, True, timeout=3600)
            
    return "Content healing tamamlandı."


@shared_task
def trigger_description_auto_healing():
    category_name = "empty description"
    time_threshold = timezone.now() - timedelta(minutes=30)
    problems = Problem.objects.filter(
        category__category=category_name, 
        is_deleted=False,
        created_at__gte=time_threshold
    )
    
    for problem in problems:
        source_id = problem.source_id
        cache_key = f"healer_processed_{source_id}_{category_name}"
        
        if cache.get(cache_key):
            continue

        if not problem.problem_description:
            continue
            
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            continue

        articles = problem_desc.get("articles", [])
        urls_to_test = [article.get("url") for article in articles if article.get("url")][:5]

        if urls_to_test:
            healer = DescriptionAutoHealer(source_id=source_id, test_urls=urls_to_test)
            result = healer.run_diagnostics()
            
            if result and isinstance(result, dict):
                resolution_type = result.get("resolution_type")
                rule_content = result.get("rule")
                
                if resolution_type and rule_content:
                    SourceRule.objects.filter(
                        problem__source_id=source_id, 
                        problem__category__category=category_name,
                        is_active=True
                    ).update(is_active=False)
                    
                    SourceRule.objects.create(
                        problem=problem,
                        resolution_type=resolution_type,
                        rule_content=rule_content,
                        is_active=True
                    )
                    print(f"{rule_content} qaydası ilə {resolution_type} həll edildi.")
            
            cache.set(cache_key, True, timeout=3600)
            
    return "Description healing tamamlandı."




@shared_task
def trigger_shared_date_auto_healing():
    category_name = "empty shared time"
    time_threshold = timezone.now() - timedelta(minutes=30)
    problems = Problem.objects.filter(
        category__category=category_name, 
        is_deleted=False,
        created_at__gte=time_threshold
    )
    
    for problem in problems:
        source_id = problem.source_id
        cache_key = f"healer_processed_{source_id}_{category_name}"
        
        if cache.get(cache_key):
            continue

        if not problem.problem_description:
            continue
            
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            continue

        articles = problem_desc.get("articles", [])
        urls_to_test = [article.get("url") for article in articles if article.get("url")][:5]

        if urls_to_test:
            healer = SharedDateAutoHealer(source_id=source_id, test_urls=urls_to_test)
            result = healer.run_diagnostics()
            
            if result and isinstance(result, dict):
                resolution_type = result.get("resolution_type")
                rule_content = result.get("rule")
                
                if resolution_type and rule_content:
                    SourceRule.objects.filter(
                        problem__source_id=source_id, 
                        problem__category__category=category_name,
                        is_active=True
                    ).update(is_active=False)
                    
                    SourceRule.objects.create(
                        problem=problem,
                        resolution_type=resolution_type,
                        rule_content=rule_content,
                        is_active=True
                    )
                    print(f"{rule_content} qaydası ilə {resolution_type} həll edildi.")
            
            cache.set(cache_key, True, timeout=3600)
            
    return "Shared time healing tamamlandı."