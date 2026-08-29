"""Enhancement perturbers using PIL."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.photometric._enhance.brightness_perturber import (
        BrightnessPerturber as BrightnessPerturber,
    )
    from nrtk.impls.perturb_image.photometric._enhance.color_perturber import (
        ColorPerturber as ColorPerturber,
    )
    from nrtk.impls.perturb_image.photometric._enhance.contrast_perturber import (
        ContrastPerturber as ContrastPerturber,
    )
    from nrtk.impls.perturb_image.photometric._enhance.sharpness_perturber import (
        SharpnessPerturber as SharpnessPerturber,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "BrightnessPerturber": "nrtk.impls.perturb_image.photometric._enhance.brightness_perturber",
                "ColorPerturber": "nrtk.impls.perturb_image.photometric._enhance.color_perturber",
                "ContrastPerturber": "nrtk.impls.perturb_image.photometric._enhance.contrast_perturber",
                "SharpnessPerturber": "nrtk.impls.perturb_image.photometric._enhance.sharpness_perturber",
            },
            extras=["pillow"],
        ),
    ],
)
