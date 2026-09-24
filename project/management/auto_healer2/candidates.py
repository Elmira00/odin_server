
#odin2/project/management/auto_healer/candidates.py
"""
Shared candidate representation and scoring.

Both the base algorithm (resolvers.py) and every helper produce Candidate
objects through this same module. Nothing downstream cares who produced a
candidate -- validation and scoring are identical regardless of source,
which is what keeps helpers from turning into special-cased branches.
"""
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Candidate:
    field: str                      # "title" | "description" | "content" | "image" | "shared_date"
    resolution_type: str            # "css_selector" | "meta" | "json_ld" | "api_json"
    rule: Any                       # selector string, meta mapping dict, or API path spec
    source: str                     # "base" or the helper's name, e.g. "wordpress_api"
    node: Optional[object] = None   # the actual bs4 node, if this came from DOM search (for scoring)
    value: Optional[str] = None     # the actual extracted value, if this came from an API/JSON source
    prior_confidence: float = 0.5   # how much this producer trusts itself, before validation


def link_density(node) -> float:
    text_len = len(node.get_text(strip=True))
    if text_len == 0:
        return 1.0
    link_len = sum(len(a.get_text(strip=True)) for a in node.find_all('a'))
    return link_len / text_len


def validate_candidate(candidate: Candidate) -> bool:
    """One shared validation gate for every candidate, regardless of producer.
    Field-specific sanity rules live here so a helper can't bypass them by
    being clever -- if it doesn't pass this, it doesn't get scored at all.
    """
    if candidate.resolution_type in ("meta", "json_ld", "api_json"):
        val = candidate.value
        if not val or not str(val).strip():
            return False
        if candidate.field == "description" and len(str(val).strip()) < 15:
            return False
        if candidate.field in ("title", "shared_date") and len(str(val).strip()) < 3:
            return False
        return True

    # css_selector / DOM-node candidates
    node = candidate.node
    if node is None:
        return False

    if candidate.field == "content":
        # Delegates to the single canonical implementation shared with
        # resolvers.py's ContentAutoHealer -- see content_signals.py.
        from management.auto_healer.content_signals import validate_content_node
        return validate_content_node(node)

    from management.auto_healer.content_signals import NOISE_WRAPPER_HINTS, classes_for_noise_check
    classes = classes_for_noise_check(node)
    if NOISE_WRAPPER_HINTS.search(classes):
        return False
    if node.find_parent(['nav', 'footer', 'aside', 'header']):
        return False

    text_len = len(node.get_text(strip=True))

    if candidate.field == "title":
        return 3 <= text_len <= 300

    if candidate.field == "description":
        return text_len >= 15

    if candidate.field == "image":
        return True  # image candidates are validated at the src level upstream

    if candidate.field == "shared_date":
        return text_len > 0 or node.has_attr('datetime')

    return True


def score_candidate(candidate: Candidate) -> float:
    """Combine producer confidence with cheap structural signal. Kept simple
    on purpose -- the ensemble-agreement step in discovery.py does the real
    heavy lifting; this is just a tiebreaker among already-valid candidates.
    """
    score = candidate.prior_confidence * 100

    # Structured/API sources outrank DOM guesses when both are valid.
    if candidate.resolution_type in ("json_ld", "api_json"):
        score += 40
    elif candidate.resolution_type == "meta":
        score += 30

    if candidate.node is not None and candidate.field == "content":
        score += min(len(candidate.node.get_text(strip=True)) / 50, 20)
        score -= link_density(candidate.node) * 30

    return score