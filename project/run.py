import os
import django
from datetime import timedelta
from django.utils import timezone

# Django mühitini tənzimləyirik
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Count
from scraper.models import Source

def get_recently_active_sources():
    # Cari vaxtdan 3 gün əvvəlki nöqtəni təyin edirik
    three_days_ago = timezone.now() - timedelta(days=3)
    
    # is_active-ə baxmadan, son 3 gündə xəbəri yaranmış mənbələri tapırıq (.distinct() təkrarların qarşısını alır)
    active_sources = Source.objects.filter(
        newsarticles__created_at__gte=three_days_ago
    ).distinct()
    
    total_active_count = active_sources.count()
    
    print(f"=== SON 3 GÜNDƏ AKTİV OLAN MƏNBƏLƏRİN STATİSTİKASI ===")
    print(f"Ümumi aktiv mənbələrin sayı: {total_active_count}\n")
    
    # Həmin mənbələrin xəbər sayını hesablayırıq
    sources_data = active_sources.annotate(
        article_count=Count('newsarticles')
    ).values('id', 'name', 'link', 'article_count')
    
    print(f"{'ID':<5} | {'Mənbə Adı':<30} | {'Xəbər Sayı':<10} | {'Link'}")
    print("-" * 75)
    
    for src in sources_data:
        src_id = src['id']
        src_name = src['name'] or "Adsız Mənbə"
        article_count = src['article_count']
        src_link = src['link'] or "Link yoxdur"
        
        print(f"{src_id:<5} | {src_name[:28]:<30} | {article_count:<10} | {src_link}")

if __name__ == '__main__':
    get_recently_active_sources()
