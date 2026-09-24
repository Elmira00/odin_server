#odin2/project/management/auto_healer/helpers/base_helper.py
"""
Interface every helper implements.

A helper is keyed to a structural/platform SIGNATURE, never to a domain.
`applies()` must be a cheap, generic structural check -- if it only ever
returns True for one specific source, it doesn't belong here; it belongs
in that source's manually-confirmed registry override instead (see
registry_store.py). This file has no logic itself -- it's the contract.
"""
from abc import ABC, abstractmethod
from typing import List
from management.auto_healer.candidates import Candidate


class BaseHelper(ABC):
    name: str = "unnamed_helper"
    tier: int = 0          # 0 = cheap, always attempted; 2 = expensive, gated behind low confidence
    fields: tuple = ()      # which fields this helper can contribute to, e.g. ("title", "description")

    @abstractmethod
    def applies(self, soup) -> bool:
        """Cheap structural check. Must not depend on domain/source_id --
        only on markup shape (a JSON blob's presence, a REST link tag, etc.)."""
        raise NotImplementedError

    @abstractmethod
    def get_candidates(self, soup, field: str, url: str) -> List[Candidate]:
        """Contribute zero or more candidates for the given field. Never
        return a bare final answer -- always go through Candidate so the
        shared validate/score step in candidates.py makes the actual call."""
        raise NotImplementedError