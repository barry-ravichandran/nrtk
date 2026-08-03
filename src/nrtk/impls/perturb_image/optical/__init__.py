"""Module for optical implementations of PerturbImage."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.optical import otf as otf
    from nrtk.impls.perturb_image.optical._pybsm_perturber import PybsmPerturber as PybsmPerturber
    from nrtk.impls.perturb_image.optical._radial_distortion_perturber import (
        RadialDistortionPerturber as RadialDistortionPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    submodules=["otf"],
    groups=[
        Group(
            symbols={
                "RadialDistortionPerturber": "nrtk.impls.perturb_image.optical._radial_distortion_perturber",
            },
        ),
        Group(
            symbols={"PybsmPerturber": "nrtk.impls.perturb_image.optical._pybsm_perturber"},
            extras=["pybsm"],
        ),
    ],
)
