import logging
import hashlib
import json
from collections import defaultdict
from typing import List
from datetime import timedelta

import redis
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from celery import shared_task

from management.models import Problem, SourceRule, AutoHealerFinding
from management.auto_healer.fetching import FetchManager, PageContext
from management.auto_healer.resolvers_adapter import (
    ImageAutoHealer, TitleAutoHealer,
    ContentAutoHealer, DescriptionAutoHealer, SharedDateAutoHealer
)
from management.auto_healer.discovery import discover_field
import management.auto_healer.helpers  # noqa: F401

logger = logging.getLogger(__name__)

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
HEALER_MAP = {
    "empty image": ImageAutoHealer,
    "empty title": TitleAutoHealer,
    "empty content": ContentAutoHealer,
    "empty description": DescriptionAutoHealer,
    "empty news_shared_date": SharedDateAutoHealer  # DÜZƏLDİLDİ
}

CATEGORY_TO_FIELD = {
    "empty image": "image",
    "empty title": "title",
    "empty content": "content",
    "empty description": "description",
    "empty news_shared_date": "shared_date",  # DÜZƏLDİLDİ
}


# --- ORCHESTRATION ---

def generate_cache_key(source_id: int, category_name: str, problem_ids: List[int]) -> str:
    """Creates a cache key dependent on the exact problems evaluated."""
    id_str = "_".join(map(str, sorted(problem_ids)))
    hash_str = hashlib.md5(id_str.encode()).hexdigest()
    return f"healer_rule_{source_id}_{category_name.replace(' ', '_')}_{hash_str}"


@shared_task
def trigger_all_auto_healing():
    # Vaxt məhdudiyyətini çıxardıq ki, bazadakı bütün aktiv problemli mənbələr analizə getsin
    active_sources = Problem.objects.filter(
        is_deleted=False
    ).values_list('source_id', flat=True).distinct()

    logger.info(f"trigger_all_auto_healing: {len(active_sources)} aktiv mənbə tapıldı.")

    for source_id in active_sources:
        process_source_auto_healing.delay(source_id)


@shared_task
def process_source_auto_healing(source_id):
    lock_key = f"auto_healer_lock_{source_id}"
    lock = r.lock(lock_key, timeout=300)

    if not lock.acquire(blocking=False):
        logger.warning(f"Source {source_id} üçün proses artıq işləyir (Locked).")
        return f"Locked: {source_id}"

    try:
        problems = Problem.objects.filter(
            source_id=source_id, is_deleted=False
        ).select_related('category', 'source')

        if not problems.exists():
            return "No active problems."

        category_jobs = defaultdict(lambda: {"urls": [], "problem_ids": [], "target_problem": None})
        all_unique_urls = set()

        for problem in problems:
            category_name = problem.category.category
            if category_name not in HEALER_MAP:
                continue

            job = category_jobs[category_name]
            if len(job["urls"]) >= 5:
                continue

            try:
                desc = json.loads(problem.problem_description) if isinstance(problem.problem_description, str) else problem.problem_description
                for article in desc.get("articles", []):
                    url = article.get("url")
                    if url and url not in job["urls"]:
                        job["urls"].append(url)
                        if len(job["urls"]) >= 5:
                            break

                job["problem_ids"].append(problem.id)
                if not job["target_problem"]:
                    job["target_problem"] = problem
            except (json.JSONDecodeError, AttributeError):
                continue

        active_jobs = {}
        for cat_name, job in category_jobs.items():
            if not job["urls"]:
                continue
            cache_key = generate_cache_key(source_id, cat_name, job["problem_ids"])
            if not cache.get(cache_key):
                active_jobs[cat_name] = job
                all_unique_urls.update(job["urls"])

        if not active_jobs:
            return f"All jobs cached for source {source_id}."

        fetcher = FetchManager()
        shared_contexts = fetcher.fetch_unique_urls(all_unique_urls)

        for category_name, job in active_jobs.items():
            HealerClass = HEALER_MAP[category_name]
            field = CATEGORY_TO_FIELD[category_name]
            sample_urls = job["urls"]
            target_problem = job["target_problem"]

            logger.info(f"AutoHealer işə düşdü: {category_name} (Source: {source_id}, URLs: {len(sample_urls)})")

            compat_shared_soups = {
                url: ctx.shared_soup for url, ctx in shared_contexts.items()
                if url in sample_urls and ctx.shared_soup is not None
            }

            healer = HealerClass(source_id=source_id, test_urls=sample_urls, shared_soups=compat_shared_soups)
            discovery_result = discover_field(field, healer, compat_shared_soups)

            cache_key = generate_cache_key(source_id, category_name, job["problem_ids"])

            if discovery_result:
                res_type = discovery_result.resolution_type
                rule_content = discovery_result.rule
                
                rule_str = json.dumps(rule_content, ensure_ascii=False) if isinstance(rule_content, dict) else str(rule_content)
                evidence_json = json.dumps(sample_urls)

                try:
                    finding = AutoHealerFinding.objects.get(
                        source_id=source_id,
                        category=target_problem.category,
                        resolution_type=res_type,
                        rule_content=rule_str
                    )
                    
                    if finding.status == 'PENDING':
                        finding.confidence = discovery_result.confidence
                        finding.evidence_urls = evidence_json
                        finding.save(update_fields=['confidence', 'evidence_urls', 'updated_at'])
                        logger.info(f"Mövcud PENDING finding yeniləndi: Source {source_id}, {category_name}")
                    else:
                        logger.info(f"Qayda artıq {finding.status} vəziyyətindədir - keçildi.")
                
                except AutoHealerFinding.DoesNotExist:
                    AutoHealerFinding.objects.create(
                        source=target_problem.source,
                        category=target_problem.category,
                        resolution_type=res_type,
                        rule_content=rule_str,
                        confidence=discovery_result.confidence,
                        evidence_urls=evidence_json,
                        status='PENDING'
                    )
                    logger.info(f"YENİ FINDING YARADILDI: Source {source_id}, {category_name}, Confidence: {discovery_result.confidence:.1f}%")
                
                cache.set(cache_key, True, timeout=3600)
            else:
                logger.info(f"Qayda tapılmadı və ya qəbul edilmədi: {category_name} (Source {source_id})")
                cache.set(cache_key, True, timeout=900)

        return f"Processed {source_id} successfully."
    finally:
        lock.release()