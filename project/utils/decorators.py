from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from scraper.models import Source

def check_source_active(source_link: str):
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                source = Source.objects.get(link=source_link)
            except ObjectDoesNotExist:
                print(f"[❌] Source is not found: {source_link}")
                return None

            if not source.is_active:
                return None

            return func(*args, **kwargs)
        return wrapper
    return decorator
