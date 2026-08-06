"""Module for generative implementations of PerturbImage."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.generative._diffusion_perturber import (
        DiffusionPerturber as DiffusionPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={"DiffusionPerturber": "nrtk.impls.perturb_image.generative._diffusion_perturber"},
            extras=["diffusion"],
        ),
    ],
)
