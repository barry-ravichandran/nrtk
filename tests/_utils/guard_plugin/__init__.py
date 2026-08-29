"""A guarded package standing in for a real one, for the discovery checks.

Declares one experimental implementation with no extras, which is the combination
``tests/scripts/guard/discovery_across_opt_in.py`` needs: gated behind
``nrtk.experimental``, but importable in an environment with nothing optional
installed.

It exists so that check does not have to name a real NRTK implementation. The only
implementation that would qualify is temporary -- once the video work graduates
there may be none left -- and a check of the guard's own machinery should not
depend on what NRTK happens to ship.

Registered under ``smqtk_plugins`` at runtime by a synthetic distribution the
script writes, so nothing here reaches the published package.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from tests._utils.guard_plugin._impl import GuardedThingImpl as GuardedThingImpl

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(symbols={"GuardedThingImpl": "tests._utils.guard_plugin._impl"}, experimental=True),
    ],
)
