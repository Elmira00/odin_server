# project/management/auto_healer/discovery.py
"""
Orchestrates one discovery run for a single field across sample URLs.

Flow: tier-0 helpers + base algorithm run unconditionally -> score -> 
if confident, return -> else run tier-2 helpers -> re-evaluate.
Relaxed for human-in-the-loop review queue.
"""
from collections import Counter
from management.auto_healer.candidates import Candidate, validate_candidate, score_candidate
from management.auto_healer.helpers.registry import get_applicable_helpers

# Human-review üçün həddi yumşaldırıq (əvvəl 60.0 idi)
CONFIDENCE_THRESHOLD = 25.0
FIELDS = ("title", "description", "content", "image", "shared_date")


class DiscoveryResult:
    def __init__(self, field, resolution_type, rule, confidence, sample_count, agreeing_sources):
        self.field = field
        self.resolution_type = resolution_type
        self.rule = rule
        self.confidence = confidence
        self.sample_count = sample_count
        self.agreeing_sources = agreeing_sources  # e.g. {"base", "wordpress_api"}

    def to_registry_dict(self):
        return {
            "resolution_type": self.resolution_type,
            "rule": self.rule,
            "confidence": self.confidence,
            "sample_count": self.sample_count,
            "agreeing_sources": sorted(self.agreeing_sources),
        }


def discover_field(field, base_healer, soups_by_url: dict) -> DiscoveryResult | None:
    """base_healer: an instance of the existing per-field healer from
    resolvers.py, adapted to expose get_base_candidates(soup, url) -> list[Candidate]
    instead of returning a final rule directly (see resolvers_adapter.py).
    """
    all_candidates = []

    for url, soup in soups_by_url.items():
        # Tier 0: helpers that structurally match this page, always attempted.
        for helper in get_applicable_helpers(soup, field, tier=0):
            all_candidates.extend(helper.get_candidates(soup, field, url))

        # Base algorithm, always attempted.
        all_candidates.extend(base_healer.get_base_candidates(soup, field, url))

    valid = [c for c in all_candidates if validate_candidate(c)]
    result = _pick_winner(field, valid, total_urls=len(soups_by_url))

    if result and result.confidence >= CONFIDENCE_THRESHOLD:
        return result

    # Tier 2: fallback helpers (əvvəlki həll 25.0-dan aşağı qaldıqda və ya tapılmadıqda)
    for url, soup in soups_by_url.items():
        for helper in get_applicable_helpers(soup, field, tier=2):
            all_candidates.extend(helper.get_candidates(soup, field, url))

    valid = [c for c in all_candidates if validate_candidate(c)]
    result_fallback = _pick_winner(field, valid, total_urls=len(soups_by_url))

    # Əgər hər hansı bir etibarlı qayda tapılıbsa, hətta confidence aşağı olsa belə insan baxışına göndərilir
    if result_fallback:
        return result_fallback

    return result


def _pick_winner(field, valid_candidates, total_urls) -> DiscoveryResult | None:
    if not valid_candidates:
        return None

    def rule_key(c):
        return (c.resolution_type, str(c.rule))

    groups = {}
    for c in valid_candidates:
        key = rule_key(c)
        groups.setdefault(key, []).append(c)

    scored_groups = []
    for key, members in groups.items():
        best_score = max(score_candidate(c) for c in members)
        distinct_sources = {c.source for c in members}
        distinct_urls_covered = len(members)
        agreement_bonus = (len(distinct_sources) - 1) * 20 + min(distinct_urls_covered, total_urls) * 5
        scored_groups.append((best_score + agreement_bonus, key, members, distinct_sources))

    scored_groups.sort(key=lambda x: x[0], reverse=True)
    top_score, top_key, top_members, top_sources = scored_groups[0]

    resolution_type, rule_str = top_key
    rule = top_members[0].rule

    # Minimum reytinqi 10.0-a bağlayırıq ki, insana görünən confidence məntiqli olsun
    confidence = min(max(top_score, 10.0), 100.0)

    return DiscoveryResult(
        field=field,
        resolution_type=resolution_type,
        rule=rule,
        confidence=confidence,
        sample_count=len(top_members),
        agreeing_sources=top_sources,
    )