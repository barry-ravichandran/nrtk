"""Module for environment implementations of PerturbImage."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.environment._haze_perturber import HazePerturber as HazePerturber
    from nrtk.impls.perturb_image.environment._water_droplet_perturber import (
        WaterDropletPerturber as WaterDropletPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(symbols={"HazePerturber": "nrtk.impls.perturb_image.environment._haze_perturber"}),
        Group(
            symbols={
                "WaterDropletPerturber": "nrtk.impls.perturb_image.environment._water_droplet_perturber",
            },
            extras=["waterdroplet"],
        ),
    ],
)
