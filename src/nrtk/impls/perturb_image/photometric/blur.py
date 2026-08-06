"""Blur perturbers using cv2."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.photometric._blur.average_blur_perturber import (
        AverageBlurPerturber as AverageBlurPerturber,
    )
    from nrtk.impls.perturb_image.photometric._blur.gaussian_blur_perturber import (
        GaussianBlurPerturber as GaussianBlurPerturber,
    )
    from nrtk.impls.perturb_image.photometric._blur.median_blur_perturber import (
        MedianBlurPerturber as MedianBlurPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "AverageBlurPerturber": "nrtk.impls.perturb_image.photometric._blur.average_blur_perturber",
                "GaussianBlurPerturber": "nrtk.impls.perturb_image.photometric._blur.gaussian_blur_perturber",
                "MedianBlurPerturber": "nrtk.impls.perturb_image.photometric._blur.median_blur_perturber",
            },
            extras=[("graphics", "headless")],
        ),
    ],
)
