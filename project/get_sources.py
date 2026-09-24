import os
import django
from datetime import timedelta
from django.utils import timezone

# Django mühitini quraşdırırıq
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from management.models import Source, NewsArticle 

def show_recently_scraped_sources(days=10):
    try:
        # Son 'days' günün vaxtını tapırıq
        time_threshold = timezone.now() - timedelta(days=days)

        # Son 10 gündə scrape edilmiş NewsArticle-ların source ID-lərini tapırıq
        recent_source_ids = NewsArticle.objects.filter(
            created_at__gte=time_threshold
        ).values_list('source_id', flat=True).distinct()

        # Tapılmış ID-lər əsasında Source obyektlərini çəkirik
        active_sources = Source.objects.filter(id__in=recent_source_ids)

        count = active_sources.count()
        print(f"\n=== SON {days} GÜNDƏ REALLIQDA SCRAPE EDİLMİŞ {count} MƏNBƏ (SOURCE) VAR ===\n")

        if count == 0:
             print(f"Son {days} gündə heç bir scrape qeydə alınmayıb.")
             return

        for source in active_sources:
            name = source.name if source.name else 'Ad yoxdur'
            domain = source.link if source.link else 'Domain yoxdur'

            # Platforma tipini müəyyən edirik
            if source.type == 2:
                source_type = "Telegram"
            elif source.type == 3:
                source_type = "Facebook"
            else:
                source_type = "Sayt"

            # Əlavə məlumat: Həmin mənbədən son X gündə neçə məqalə scrape edilib?
            article_count = NewsArticle.objects.filter(
                source_id=source.id,
                created_at__gte=time_threshold
            ).count()

            print(f"ID: {source.id:<4} | Tip: {source_type:<10} | Ad: {name:<25} | Son {days} gündə: {article_count:<4} | Link: {domain}")

            # --- YENİ ƏLAVƏ: Ən son 6 URL-i çəkirik ---
            latest_articles = NewsArticle.objects.filter(source_id=source.id).order_by('-created_at')[:6]
            
            if latest_articles.exists():
                print("      Son 6 URL:")
                for idx, article in enumerate(latest_articles, 1):
                    print(f"        {idx}. {article.url}")
            else:
                print("      [URL tapılmadı]")
                
            print("-" * 100) # Hər mənbənin arasına xətt çəkirik ki qarışmasın

        print("\n=== YEKUN ===")

    except Exception as e:
        print(f"\n[XƏTA] Gözlənilməz xəta: {e}")

if __name__ == "__main__":
    show_recently_scraped_sources(days=10)
