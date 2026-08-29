"""Module for all PerturbImage implementations."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image._albumentations.albumentations_perturber import (
        AlbumentationsPerturber as AlbumentationsPerturber,
    )
    from nrtk.impls.perturb_image._compose_perturber import ComposePerturber as ComposePerturber

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    submodules=["geometric", "photometric", "environment", "optical", "generative"],
    groups=[
        Group(symbols={"ComposePerturber": "nrtk.impls.perturb_image._compose_perturber"}),
        Group(
            symbols={
                "AlbumentationsPerturber": "nrtk.impls.perturb_image._albumentations.albumentations_perturber",
            },
            # albumentations needs an OpenCV build, and either one will do. There is
            # no pip spec for that, which is why the requirement is expressed here.
            extras=["albumentations", ("graphics", "headless")],
        ),
    ],
)
