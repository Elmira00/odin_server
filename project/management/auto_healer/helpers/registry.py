#project/management/auto_healer/helpers/registry.py
"""
Helper registry. Adding a new helper means writing one file that
subclasses BaseHelper and decorates itself with @register_helper --
nothing in resolvers.py or discovery.py needs to change.
"""
from typing import List, Type
from management.auto_healer.helpers.base_helper import BaseHelper

_REGISTERED_HELPERS: List[Type[BaseHelper]] = []


def register_helper(cls: Type[BaseHelper]) -> Type[BaseHelper]:
    _REGISTERED_HELPERS.append(cls)
    return cls


def get_helpers_for_field(field: str, tier: int = None) -> List[BaseHelper]:
    helpers = [cls() for cls in _REGISTERED_HELPERS if field in cls.fields]
    if tier is not None:
        helpers = [h for h in helpers if h.tier == tier]
    return helpers


def get_applicable_helpers(soup, field: str, tier: int = None) -> List[BaseHelper]:
    """Run each candidate helper's cheap applies() check and return only
    the ones that actually match this page's structure."""
    return [h for h in get_helpers_for_field(field, tier) if h.applies(soup)]