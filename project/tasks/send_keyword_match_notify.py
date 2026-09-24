# tasks_telegram_redis.py



from celery import shared_task
from django.db import transaction
from collections import defaultdict
from django.conf import settings
from telethon import TelegramClient, events
import requests
from .models import KeywordsNewsArticleCombination,TempDataEmail,TempDataTelegram,TelegramUser
from scraper.models import NewsArticle
from datetime import datetime
import hashlib
import redis
import json
import time
import asyncio
from asgiref.sync import sync_to_async  
from django.core.mail import send_mail
import threading
from telethon.sessions import StringSession, SQLiteSession
from django.core.cache import caches
from utils.check_keyword import get_all_keywords
import json

redis_cache = caches["redis"]
CACHE_KEY = "odin_keywords"


# ------------------------
# Redis konfiqurasiya
# ------------------------
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 2
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


EMAIL_ENDPOINT = "http://ophrys.local/api/users/emails"
TELEGRAM_ENDPOINT = "http://ophrys.local/api/users/telegrams"


# ------------------------
# Utility functions
# ------------------------
def generate_token(salt="token"):
    current_time = datetime.now().strftime("%Y%m%d %H")
    inner_hash = hashlib.md5(current_time.encode()).hexdigest()
    final_hash = hashlib.md5((salt + inner_hash).encode()).hexdigest()
    return final_hash



# ###############################TELEGRAM$$$$$$$########################


BATCH_SIZE = 20
TELEGRAM_DELAY = 0.05


def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]


_telegram_client = None
_client_lock = asyncio.Lock()


async def get_telegram_client():
    global _telegram_client

    if _telegram_client is None:
        async with _client_lock:
            if _telegram_client is None:
                client = TelegramClient(
                    StringSession(),
                    settings.TELEGRAM_API_ID,
                    settings.TELEGRAM_API_HASH
                )
                await client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)
                _telegram_client = client

    return _telegram_client


def build_telegram_message(match_keyword_newsarticle, keywords, newsarticles=None):
    lines = ["🔔 Açar söz statistikası:\n"]

    total_count = 0

    for k_id, article_ids in match_keyword_newsarticle.items():
        keyword_name = keywords.get(str(k_id)) or str(k_id)
        count = len(article_ids)
        total_count += count

        lines.append(f'🔑 "{keyword_name}" açar sözü — {count} xəbər')

    lines.append("")
    lines.append(f"📊 Ümumi uyğun xəbər sayı: {total_count}")

    return "\n".join(lines).strip()


def fetch_telegram_data(user_ids):
    if not user_ids:
        return {}

    try:
        response = requests.post(
            TELEGRAM_ENDPOINT,
            json={"ids": user_ids},
            headers={"X-API-TOKEN": generate_token()},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return data.get("telegrams", {})

    except Exception as e:
        print("Telegram API error:", e)
        return {}


# ------------------------
# Temp telegram data build
# ------------------------
@shared_task
def build_temp_telegram_data():
    with transaction.atomic():
        qs = (
            KeywordsNewsArticleCombination.objects
            .select_for_update(skip_locked=True)
            .filter(telegram_status=True, is_telegram_processed=False)
            .values("id", "user_id", "keyword_id", "newsarticle_id")
        )

        if not qs.exists():
            print("No new telegram data")
            return

        grouped = defaultdict(lambda: defaultdict(list))
        keyword_ids = set()
        article_ids = set()
        ids = []

        for row in qs:
            ids.append(row["id"])

            u = row["user_id"]
            k = row["keyword_id"]
            a = row["newsarticle_id"]

            grouped[u][k].append(a)
            keyword_ids.add(k)
            article_ids.add(a)

        keywords_data = redis_cache.get(CACHE_KEY) or get_all_keywords()

        keyword_map = {}
        for item in keywords_data:
            for name, data in item.items():
                kid = data["id"]
                if kid in keyword_ids:
                    keyword_map[kid] = name

        articles = NewsArticle.objects.filter(id__in=article_ids).values("id", "url")
        article_map = {a["id"]: a["url"] for a in articles}

        user_ids = list(grouped.keys())
        existing_temp = TempDataTelegram.objects.filter(user_id__in=user_ids, is_send=False)
        existing_map = {t.user_id: t for t in existing_temp}

        for user_id, keyword_data in grouped.items():
            user_article_ids = {a for ids_list in keyword_data.values() for a in ids_list}

            if user_id in existing_map:
                temp_obj = existing_map[user_id]

                existing_match = json.loads(temp_obj.match_keyword_newsarticle or "{}")
                for k, articles_list in keyword_data.items():
                    k_str = str(k)
                    existing_list = existing_match.get(k_str, [])
                    existing_match[k_str] = list(set(existing_list + articles_list))

                existing_keywords = json.loads(temp_obj.keywords or "{}")
                for k in keyword_data.keys():
                    existing_keywords[str(k)] = keyword_map.get(k, str(k))

                existing_articles = json.loads(temp_obj.newsarticles or "{}")
                for a in user_article_ids:
                    existing_articles[str(a)] = article_map.get(a, "")

                temp_obj.match_keyword_newsarticle = json.dumps(existing_match, ensure_ascii=False)
                temp_obj.keywords = json.dumps(existing_keywords, ensure_ascii=False)
                temp_obj.newsarticles = json.dumps(existing_articles, ensure_ascii=False)

                temp_obj.save(update_fields=[
                    "match_keyword_newsarticle",
                    "keywords",
                    "newsarticles",
                ])

            else:
                TempDataTelegram.objects.create(
                    user_id=user_id,
                    match_keyword_newsarticle=json.dumps(
                        {str(k): v for k, v in keyword_data.items()},
                        ensure_ascii=False
                    ),
                    keywords=json.dumps(
                        {str(k): keyword_map.get(k, str(k)) for k in keyword_data},
                        ensure_ascii=False
                    ),
                    newsarticles=json.dumps(
                        {str(a): article_map.get(a, "") for a in user_article_ids},
                        ensure_ascii=False
                    ),
                )

        KeywordsNewsArticleCombination.objects.filter(
            id__in=ids
        ).update(is_telegram_processed=True)

        print("TempDataTelegram updated/created")


# ------------------------
# Async-safe DB/API wrappers
# ------------------------
@sync_to_async
def get_unsent_temp_telegrams():
    return list(
        TempDataTelegram.objects
        .filter(is_send=False)
        .only("id", "user_id", "match_keyword_newsarticle", "keywords", "newsarticles")[:200]
    )


@sync_to_async
def mark_temp_telegrams_sent(sent_ids):
    if sent_ids:
        TempDataTelegram.objects.filter(id__in=sent_ids).update(is_send=True)


@sync_to_async
def get_telegram_users_sync(user_ids):
    return fetch_telegram_data(user_ids)


# ------------------------
# Telegram send task
# ------------------------
async def _send_digest_telegrams_async():
    qs = await get_unsent_temp_telegrams()

    if not qs:
        print("Telegram yoxdur")
        return

    user_ids = [t.user_id for t in qs]
    telegram_users = await get_telegram_users_sync(user_ids)

    chat_map = {}
    for uid, info in telegram_users.items():
        if not info:
            continue

        chat_id = info.get("chat_id")
        if chat_id:
            try:
                chat_map[int(uid)] = int(chat_id)
            except (TypeError, ValueError):
                continue

    client = await get_telegram_client()
    sent_ids = []

    for batch in chunk_list(qs, BATCH_SIZE):
        for t in batch:
            chat_id = chat_map.get(t.user_id)
            if not chat_id:
                continue

            try:
                match_keyword_newsarticle = json.loads(t.match_keyword_newsarticle or "{}")
                keywords = json.loads(t.keywords or "{}")
                newsarticles = json.loads(t.newsarticles or "{}")
            except Exception as e:
                print(f"Telegram JSON parse error user_id={t.user_id}: {e}")
                continue

            message = build_telegram_message(
                match_keyword_newsarticle=match_keyword_newsarticle,
                keywords=keywords,
                newsarticles=newsarticles
            )

            try:
                await asyncio.wait_for(
                    client.send_message(chat_id, message),
                    timeout=10
                )
                sent_ids.append(t.id)
                await asyncio.sleep(TELEGRAM_DELAY)

            except Exception as e:
                print(f"Telegram error user_id={t.user_id}: {e}")

        await asyncio.sleep(0.5)

    await mark_temp_telegrams_sent(sent_ids)
    print(f"{len(sent_ids)} telegram queue-ya verildi")


@shared_task
def send_digest_telegrams():
    asyncio.run(_send_digest_telegrams_async())


# ------------------------
# Bot listener (async)
# ------------------------
async def start_bot_listener():
    client = await get_telegram_client()

    @client.on(events.NewMessage(pattern="/start"))
    async def handler(event):
        chat_id = str(event.chat_id)
        sender = await event.get_sender()
        username = sender.username

        if not username:
            await event.respond("Telegram username yoxdur.")
            return

        payload = {
            "username": username,
            "chat_id": chat_id
        }

        await event.respond(json.dumps(payload, ensure_ascii=False))
        print(payload)

    print("Telegram bot listener started")
    await client.run_until_disconnected()





##################EMAIL GOnderme##############



import os
from datetime import datetime

DEBUG_EMAIL_FILE = "/tmp/odin_email_debug.log"

def write_email_debug(email, body, error=None):
    with open(DEBUG_EMAIL_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n============================\n")
        f.write(f"TIME: {datetime.now()}\n")
        f.write(f"EMAIL: {email}\n")
        if error:
            f.write(f"ERROR: {error}\n")
        f.write("\nEMAIL BODY:\n")
        f.write(body)
        f.write("\n============================\n")

# ------------------------
# Email göndərmə task
# ------------------------
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, max_retries=5)
def send_email_task(self, email, body):
    write_email_debug(email, body)
    try:
        send_mail(
            subject=f"Odin-Monitorinq açar söz bildirişi (Tarix: {datetime.now().strftime('%d.%m.%Y')})",
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        write_email_debug(email, body, str(e))
        print(f"Mail send error for {email}: {e}")
        raise e

# ------------------------
# Temp email data build
# ------------------------
@shared_task
def build_temp_mail_data():
    with transaction.atomic():

        qs = (
            KeywordsNewsArticleCombination.objects
            .select_for_update(skip_locked=True)
            .filter(email_status=True, is_email_processed=False)
            .values("id", "user_id", "keyword_id", "newsarticle_id")
        )

        if not qs.exists():
            print("No new email data")
            return

        grouped = defaultdict(lambda: defaultdict(list))
        keyword_ids = set()
        article_ids = set()
        ids = []

        for row in qs:
            ids.append(row["id"])
            u = row["user_id"]
            k = row["keyword_id"]
            a = row["newsarticle_id"]

            grouped[u][k].append(a)
            keyword_ids.add(k)
            article_ids.add(a)

        # Keyword map
        keywords_data = redis_cache.get(CACHE_KEY) or get_all_keywords()
        keyword_map = {}
        for item in keywords_data:
            for name, data in item.items():
                kid = data["id"]
                if kid in keyword_ids:
                    keyword_map[kid] = name

        # Article map
        articles = NewsArticle.objects.filter(id__in=article_ids).values("id", "url")
        article_map = {a["id"]: a["url"] for a in articles}

        # Existing temp data
        user_ids = list(grouped.keys())
        existing_temp = TempDataEmail.objects.filter(user_id__in=user_ids, is_send=False)
        existing_map = {t.user_id: t for t in existing_temp}

        for user_id, keyword_data in grouped.items():
            user_article_ids = {a for ids_list in keyword_data.values() for a in ids_list}

            if user_id in existing_map:
                temp_obj = existing_map[user_id]

                # 🔹 Merge match_keyword_newsarticle (TextField-safe)
                existing_match = json.loads(temp_obj.match_keyword_newsarticle or "{}")
                for k, articles_list in keyword_data.items():
                    k_str = str(k)
                    if k_str in existing_match:
                        existing_match[k_str] = list(set(existing_match[k_str] + articles_list))
                    else:
                        existing_match[k_str] = articles_list

                # 🔹 Merge keywords
                existing_keywords = json.loads(temp_obj.keywords or "{}")
                for k in keyword_data.keys():
                    existing_keywords[str(k)] = keyword_map.get(k, str(k))

                # 🔹 Merge articles
                existing_articles = json.loads(temp_obj.newsarticles or "{}")
                for a in user_article_ids:
                    existing_articles[str(a)] = article_map.get(a, "")

                # 🔹 Save back as JSON string
                temp_obj.match_keyword_newsarticle = json.dumps(existing_match)
                temp_obj.keywords = json.dumps(existing_keywords)
                temp_obj.newsarticles = json.dumps(existing_articles)

                temp_obj.save(update_fields=["match_keyword_newsarticle", "keywords", "newsarticles"])

            else:
                TempDataEmail.objects.create(
                    user_id=user_id,
                    match_keyword_newsarticle=json.dumps({str(k): v for k, v in keyword_data.items()}),
                    keywords=json.dumps({str(k): keyword_map.get(k, str(k)) for k in keyword_data}),
                    newsarticles=json.dumps({str(a): article_map.get(a, "") for a in user_article_ids}),
                )

        # Mark processed
        KeywordsNewsArticleCombination.objects.filter(id__in=ids).update(is_email_processed=True)
        print("TempDataEmail updated/created")

# ------------------------
# User email-ləri API-dən götürür
# ------------------------
def get_user_emails(user_ids):
    try:
        response = requests.post(
            EMAIL_ENDPOINT,
            json={"ids": user_ids},
            headers={"X-API-TOKEN": generate_token()}
        )
        response.raise_for_status()
        return response.json().get('emails', {})
    except Exception as e:
        print("Email service error:", e)
        return {}

# ------------------------
# Email göndərmə (TextField-safe)
# ------------------------
@shared_task
def send_digest_emails():
    qs = (
        TempDataEmail.objects
        .filter(is_send=False)
        .only("id", "user_id", "match_keyword_newsarticle", "keywords", "newsarticles")[:200]
    )

    if not qs.exists():
        print("Email yoxdur")
        return

    user_ids = list(qs.values_list("user_id", flat=True))
    user_emails = get_user_emails(user_ids)
    sent_ids = []

    for t in qs:
        email = user_emails.get(str(t.user_id))
        if not email:
            continue

        lines = ["Sizin açar sözləriniz aşağıdakı məqalələrdə keçdi:\n"]

        match_keyword_newsarticle = json.loads(t.match_keyword_newsarticle or "{}")
        keywords = json.loads(t.keywords or "{}")
        newsarticles = json.loads(t.newsarticles or "{}")

        # 🔹 Keyword üzrə siyahı
        for k_id, article_ids in match_keyword_newsarticle.items():
            keyword_name = keywords.get(str(k_id)) or str(k_id)
            lines.append(f'"{keyword_name}" açar sözü:\n')

            for i, a_id in enumerate(article_ids, 1):
                url = newsarticles.get(str(a_id))
                if url:
                    lines.append(f"{i}) {url}")
            lines.append("")

        body = "\n".join(lines)
        send_email_task.delay(email, body)
        sent_ids.append(t.id)

    if sent_ids:
        TempDataEmail.objects.filter(id__in=sent_ids).update(is_send=True)
    print(f"{len(sent_ids)} email queue-ya verildi")
