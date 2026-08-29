"""Random geometric perturbers."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image._albumentations.random_rotation_perturber import (
        RandomRotationPerturber as RandomRotationPerturber,
    )
    from nrtk.impls.perturb_image._albumentations.random_scale_perturber import (
        RandomScalePerturber as RandomScalePerturber,
    )
    from nrtk.impls.perturb_image.geometric._random.random_crop_perturber import (
        RandomCropPerturber as RandomCropPerturber,
    )
    from nrtk.impls.perturb_image.geometric._random.random_translation_perturber import (
        RandomTranslationPerturber as RandomTranslationPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "RandomCropPerturber": "nrtk.impls.perturb_image.geometric._random.random_crop_perturber",
                "RandomTranslationPerturber": (
                    "nrtk.impls.perturb_image.geometric._random.random_translation_perturber"
                ),
            },
        ),
        Group(
            symbols={
                "RandomRotationPerturber": "nrtk.impls.perturb_image._albumentations.random_rotation_perturber",
                "RandomScalePerturber": "nrtk.impls.perturb_image._albumentations.random_scale_perturber",
            },
            extras=["albumentations", ("graphics", "headless")],
        ),
    ],
)
