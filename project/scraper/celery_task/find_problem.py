import json
from datetime import timedelta

from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone
from django.core.cache import cache

from management.models import Category, Problem
from scraper.models import Exclude, NewsArticle, NewsImage, Source

#six_minutes_ago = timezone.now() - timedelta(minutes=6)
MAX_PROBLEM_COUNT = 200
PROBLEM_COUNT = 10  


def create_or_update_problem(source, category_name, current_articles, category_map, condition=None):
    category = category_map.get(category_name)
    if not category:
        return

    problem = Problem.objects.filter(
        source=source,
        category=category,
        is_deleted=False
    ).first()

    problem_desc = {}
    if problem and problem.problem_description:
        try:
            problem_desc = (
                json.loads(problem.problem_description)
                if isinstance(problem.problem_description, str)
                else problem.problem_description
            )
        except json.JSONDecodeError:
            problem_desc = {}


    existing_articles = problem_desc.get("articles", [])
    existing_ids = [a["id"] for a in existing_articles]

    still_broken_articles = []
    if existing_ids:
        if condition is not None:
            still_broken_articles = list(
                NewsArticle.objects.filter(id__in=existing_ids)
                .filter(condition)
                .values("id", "url")
            )
        elif category_name == "too many changednewsarticles":
            still_broken_articles = list(
                NewsArticle.objects.filter(id__in=existing_ids)
                .annotate(changed_count=Count("changednewsarticles"))
                .filter(changed_count__gt=10)
                .values("id", "url", "changed_count")
            )
        else:
            still_broken_articles = existing_articles

    existing_broken_ids = {a["id"] for a in still_broken_articles}
    truly_new_articles = [a for a in current_articles if a["id"] not in existing_broken_ids]

    merged_articles = still_broken_articles + truly_new_articles
    merged_articles = merged_articles[:MAX_PROBLEM_COUNT]

    if len(merged_articles) < PROBLEM_COUNT:
        if problem:
            problem.delete() 
            
            cache_key = f"pending_problems_src_{source.id}_{category_name.replace(' ', '_')}"
            cache.set(cache_key, merged_articles, timeout=86400)
        return

    if problem:
        # problem.created_at = timezone.now()
        problem.is_sent = False
    else:
        problem = Problem(
            source=source,
            category=category,
            is_sent=False
        )

    problem.problem_description = json.dumps({
        "source_id": source.id,
        "source_name": source.name,
        "problem_type": category_name,
        "total_count": len(merged_articles),
        "articles": merged_articles,
    }, indent=2)

    problem.save()
    

def check_and_trigger_count(source, category_name, current_articles, category_map, condition=None):
    category = category_map.get(category_name)
    if not category:
        return
    problem_exists = Problem.objects.filter(
        source=source,
        category=category,
        is_deleted=False
    ).exists()

    if problem_exists:
        create_or_update_problem(source, category_name, current_articles, category_map, condition=condition)
        return

    if current_articles:
        #key=pending_15_empty_title
        cache_key = f"pending_problems_src_{source.id}_{category_name.replace(' ', '_')}"
        cached_articles = cache.get(cache_key, [])        
        cached_articles.extend(current_articles)
        unique_articles = list({a["id"]: a for a in cached_articles}.values())
        
        if len(unique_articles) >= PROBLEM_COUNT:
            create_or_update_problem(source, category_name, unique_articles, category_map, condition=condition)
            cache.delete(cache_key)
        else:
            cache.set(cache_key, unique_articles, timeout=432000)  # 5 gun saxlayir


def generate_problems():
    six_minutes_ago = timezone.now() - timedelta(minutes=6)
    valid_images = NewsImage.objects.filter(
        newsarticle=OuterRef('pk')
    ).filter(
        Q(image_url__isnull=False, image_url__gt="") | 
        Q(local_image_url__isnull=False, local_image_url__gt="")
    )

    categories = {
        "empty title": Q(title__isnull=True) | Q(title=""),
        "empty description": Q(description__isnull=True) | Q(description=""),
        "empty content": Q(content__isnull=True) | Q(content=""),
        "empty news_shared_date": Q(news_shared_date__isnull=True),
        "empty image": ~Exists(valid_images)
    }
    category_map = {c.category: c for c in Category.objects.all()}

    excludes = {
        e.source_id: set(e.fields)
        for e in Exclude.objects.exclude(fields=None)
    }

    sources = Source.objects.filter(is_active=True)

    for source in sources:   
        excluded_fields = excludes.get(source.id, set())


        

        source_articles = NewsArticle.objects.filter(
            source=source,
            created_at__gte=six_minutes_ago
        )

        for category_name, condition in categories.items():
            field_name = category_name.replace("empty ", "")
            if field_name in excluded_fields:
                continue


            articles = list(
                source_articles
                .filter(condition)
                .order_by('-created_at')  
                [10:]                   
                .values("id", "url")
            )
            
            check_and_trigger_count(source, category_name, articles, category_map, condition=condition)

        changed_articles = list(
            source_articles
            .annotate(changed_count=Count("changednewsarticles"))
            .filter(changed_count__gt=10)
            .values("id", "url", "changed_count")
        )

        check_and_trigger_count(source, "too many changednewsarticles", changed_articles, category_map, condition=None)
