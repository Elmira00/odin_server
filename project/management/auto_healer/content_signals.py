#project/management/auto_healer/content_signals.py
"""
Single source of truth for "is this DOM node a plausible article-body
container." Both resolvers.py (ContentAutoHealer's own internal find_*
methods) and candidates.py (the shared Candidate validation gate) call
INTO this module rather than each maintaining their own copy -- the
header/timestamp and related-post-teaser bugs both came from exactly this
kind of logic drifting apart between two copies. Fix it once, here.
"""
import re

NOISE_WRAPPER_HINTS = re.compile(
    r'overlay|popup|modal|cookie|banner|newsletter|related|recommend|comments|'
    r'header|byline|timestamp|dateline|share|social',
    re.IGNORECASE,
)


def classes_for_noise_check(node) -> str:
    """Join a node's class tokens for noise-keyword matching, but drop any
    token that's itself a negation (no-share, no-ads, no-sidebar). Sites
    commonly name a wrapper 'no-share' to mean "don't show share buttons
    here" -- that's a normal content-container name, and a naive
    substring/word-boundary match on 'share' still fires inside it (the
    hyphen creates its own word boundary), which would incorrectly reject
    exactly the kind of div we want to keep.
    """
    tokens = node.get('class', []) or []
    kept = [t for t in tokens if not re.match(r'^no[-_]', t, re.IGNORECASE)]
    return " ".join(kept).lower()


def has_noisy_ancestor(node) -> bool:
    """Scan every ancestor's class/id (not just the immediate parent's tag
    name) for noise keywords. A related-articles teaser card is rarely
    itself classed 'related' -- it's the wrapper several levels up (e.g.
    div.jnews_related_post_container) that carries that signal.
    """
    for ancestor in node.parents:
        if ancestor.name in ('html', '[document]'):
            break
        if getattr(ancestor, 'attrs', None) is None:
            continue
        ancestor_classes = classes_for_noise_check(ancestor)
        ancestor_id = str(ancestor.get('id', '')).lower()
        if NOISE_WRAPPER_HINTS.search(ancestor_classes) or NOISE_WRAPPER_HINTS.search(ancestor_id):
            return True
    return False


def has_duplicate_siblings(node, min_siblings: int = 2) -> bool:
    """A genuine article body is a singleton within its parent. A teaser
    card inside a related/grid/list block always has multiple siblings
    sharing the same tag+class signature -- this catches list-item noise
    even when no ancestor or class name gives it away at all.
    """
    parent = node.parent
    if parent is None:
        return False
    own_classes = frozenset(node.get('class', []) or [])
    if not own_classes:
        return False
    matching_siblings = [
        sib for sib in parent.find_all(node.name, recursive=False)
        if sib is not node and frozenset(sib.get('class', []) or []) == own_classes
    ]
    return len(matching_siblings) >= min_siblings


def link_density(node) -> float:
    text_len = len(node.get_text(strip=True))
    if text_len == 0:
        return 1.0
    link_len = sum(len(a.get_text(strip=True)) for a in node.find_all('a'))
    return link_len / text_len


def validate_content_node(node, h1_tag=None) -> bool:
    """The one canonical answer to "is this node a plausible article body."
    resolvers.py's ContentAutoHealer and candidates.py's validate_candidate
    both call this instead of keeping their own copy.
    """
    if node is None:
        return False

    classes = classes_for_noise_check(node)
    if NOISE_WRAPPER_HINTS.search(classes):
        return False
    if node.find_parent(['nav', 'footer', 'aside', 'header']):
        return False
    if has_noisy_ancestor(node):
        return False
    if has_duplicate_siblings(node):
        return False

    # Structural invariant: the article body and the headline block are
    # always distinct containers. A candidate that contains the page's own
    # h1 is a header/meta wrapper, not the body, regardless of text/paragraph
    # counts.
    if node.find('h1') is not None:
        return False

    text_len = len(node.get_text(strip=True))
    p_count = len(node.find_all('p'))
    if text_len < 200 and p_count < 2:
        return False

    # A block that's mostly a timestamp/copyright line rather than real prose
    # ("10:14 15.09.2026 (güncellendi ...) © Source") has very few
    # sentence-ending periods relative to its length -- real article
    # paragraphs don't look like this even when short.
    if p_count == 0:
        period_count = node.get_text(strip=True).count('.')
        if text_len > 0 and period_count / max(text_len, 1) < 0.003 and text_len < 400:
            return False

    if link_density(node) > 0.5 and text_len < 1000:
        return False

    return True