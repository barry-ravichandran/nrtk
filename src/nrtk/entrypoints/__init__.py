"""Command-line interface tools."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.entrypoints._nrtk_perturber import nrtk_perturber as nrtk_perturber
    from nrtk.entrypoints._nrtk_perturber_cli import nrtk_perturber_cli as nrtk_perturber_cli

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={"nrtk_perturber": "nrtk.entrypoints._nrtk_perturber"},
            extras=["maite"],
        ),
        Group(
            symbols={"nrtk_perturber_cli": "nrtk.entrypoints._nrtk_perturber_cli"},
            extras=["maite", "tools"],
        ),
    ],
)
