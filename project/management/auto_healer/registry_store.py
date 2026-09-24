#project/management/auto_healer/registry_store.py
"""
Per-(source, field) persisted resolution rules. Discovery runs once per
source; extraction reads from here on every scrape instead of re-guessing.

Swap the storage backend (this sketch uses a Django model shape in comments)
for whatever you're actually running on -- the interface is what matters.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RegistryEntry:
    source_id: int
    field: str
    resolution_type: str
    rule: dict
    confidence: float
    agreeing_sources: list
    discovered_at: str
    last_validated_at: Optional[str] = None
    consecutive_failures: int = 0
    manually_confirmed: bool = False  # set True once a human approves a low-confidence result


class SelectorRegistry:
    """
    Backing store sketch -- in Django this would be a model:

        class ResolverRule(models.Model):
            source_id = models.IntegerField()
            field = models.CharField(max_length=32)
            resolution_type = models.CharField(max_length=32)
            rule = models.JSONField()
            confidence = models.FloatField()
            agreeing_sources = models.JSONField(default=list)
            discovered_at = models.DateTimeField(auto_now_add=True)
            last_validated_at = models.DateTimeField(null=True)
            consecutive_failures = models.IntegerField(default=0)
            manually_confirmed = models.BooleanField(default=False)

            class Meta:
                unique_together = ("source_id", "field")
    """

    def __init__(self, backend=None):
        self._backend = backend or {}  # {(source_id, field): RegistryEntry}

    def get(self, source_id: int, field: str) -> Optional[RegistryEntry]:
        return self._backend.get((source_id, field))

    def save_discovery(self, source_id: int, field: str, discovery_result) -> RegistryEntry:
        entry = RegistryEntry(
            source_id=source_id,
            field=field,
            resolution_type=discovery_result.resolution_type,
            rule=discovery_result.rule,
            confidence=discovery_result.confidence,
            agreeing_sources=sorted(discovery_result.agreeing_sources),
            discovered_at=datetime.now(timezone.utc).isoformat(),
            manually_confirmed=discovery_result.confidence >= 90,
        )
        self._backend[(source_id, field)] = entry
        return entry

    def needs_review(self, source_id: int, field: str) -> bool:
        entry = self.get(source_id, field)
        return entry is not None and not entry.manually_confirmed and entry.confidence < 90

    def record_extraction_result(self, source_id: int, field: str, success: bool):
        entry = self.get(source_id, field)
        if not entry:
            return
        entry.last_validated_at = datetime.now(timezone.utc).isoformat()
        entry.consecutive_failures = 0 if success else entry.consecutive_failures + 1

    def needs_rediscovery(self, source_id: int, field: str, failure_threshold: int = 3) -> bool:
        entry = self.get(source_id, field)
        return entry is not None and entry.consecutive_failures >= failure_threshold