import requests
import hashlib
from datetime import datetime

from django.db import transaction
from django.core.cache import caches

redis_cache = caches["redis"]

from tasks.models import KeywordsNewsArticleCombination


KEYWORDS_ENDPOINT = "http://ophrys.local/api/odin/keywords"

CACHE_KEY = "odin_keywords"
CACHE_TIMEOUT = 1200  



def generate_token(salt="token"):
    current_time = datetime.now().strftime("%Y%m%d %H")

    inner_hash = hashlib.md5(current_time.encode()).hexdigest()

    final_hash = hashlib.md5((salt + inner_hash).encode()).hexdigest()

    return final_hash




def get_all_keywords():
    cached_keywords = redis_cache.get(CACHE_KEY)

    if cached_keywords:
        return cached_keywords  # ✅ artıq deserialize olunmuş gəlir

    try:
        response = requests.post(
            KEYWORDS_ENDPOINT,
            headers={"X-API-TOKEN": generate_token()}
        )

        response.raise_for_status()

        data = response.json()

        # 🔥 IMPORTANT: plain python object save edirik
        redis_cache.set(CACHE_KEY, data, CACHE_TIMEOUT)

        return data

    except Exception as e:
        print("Keyword service error:", e)
        return []



def check_keywords_for_article(newsarticle):

    raw_text = " ".join([
        newsarticle.title or "",
        newsarticle.description or "",
        newsarticle.content or ""
    ]).lower()

    keywords_data = get_all_keywords()

    if not keywords_data:
        return

    existing_pairs = set(
        KeywordsNewsArticleCombination.objects.filter(
            newsarticle_id=newsarticle.id
        ).values_list("keyword_id", "user_id")
    )

    combination_bulk = []

    for item in keywords_data:

        for keyword, keyword_data in item.items():

            if keyword not in raw_text:
                continue

            keyword_id = keyword_data["id"]
            users = keyword_data.get("users", [])

            for user in users:

                user_id = user["user_id"]
                email_status = user.get("email", False)      
                telegram_status = user.get("telegram", False) 

                if (keyword_id, user_id) in existing_pairs:
                    continue

                combination_bulk.append(
                    KeywordsNewsArticleCombination(
                        keyword_id=keyword_id,
                        newsarticle_id=newsarticle,
                        user_id=user_id,
                        email_status=email_status,         # FIX
                        telegram_status=telegram_status,   # FIX
                        is_email_processed=False,
                        is_telegram_processed=False
                    )
                )

    if combination_bulk:
        with transaction.atomic():
            KeywordsNewsArticleCombination.objects.bulk_create(
                combination_bulk,
                batch_size=500
            )
