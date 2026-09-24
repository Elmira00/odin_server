#odin2/project/management/auto_healer/__init__.py
"""
Importing this package registers every helper via each module's
@register_helper decorator (or explicit register_helper(...) call). Any
code that wants the helper system active should do:

    import management.auto_healer.helpers  # noqa: F401

...once, before calling discover_field(). Without this import, the
registry stays empty and every helper silently never fires -- there is no
error, just base-algorithm-only results, which is exactly the failure mode
that motivated centralizing registration here instead of leaving every
caller (trigger_healer.py, tasks.py, future scripts) responsible for
importing each helper file individually.

Adding a new helper: write the file, register it inside with
@register_helper (see base_helper.py / registry.py), then add one import
line below. Nothing else needs to change.
"""
from management.auto_healer.helpers import wordpress_helper   # noqa: F401
from management.auto_healer.helpers import nextjs_helper      # noqa: F401
from management.auto_healer.helpers import lentaz_helper      # noqa: F401
# from management.auto_healer.helpers import amp_helper       # add once implemented