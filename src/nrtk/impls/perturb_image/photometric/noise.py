"""Random noise perturbers using skimage."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.photometric._noise.gaussian_noise_perturber import (
        GaussianNoisePerturber as GaussianNoisePerturber,
    )
    from nrtk.impls.perturb_image.photometric._noise.pepper_noise_perturber import (
        PepperNoisePerturber as PepperNoisePerturber,
    )
    from nrtk.impls.perturb_image.photometric._noise.salt_and_pepper_noise_perturber import (
        SaltAndPepperNoisePerturber as SaltAndPepperNoisePerturber,
    )
    from nrtk.impls.perturb_image.photometric._noise.salt_noise_perturber import (
        SaltNoisePerturber as SaltNoisePerturber,
    )
    from nrtk.impls.perturb_image.photometric._noise.speckle_noise_perturber import (
        SpeckleNoisePerturber as SpeckleNoisePerturber,
    )

_NOISE = "nrtk.impls.perturb_image.photometric._noise"

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "GaussianNoisePerturber": f"{_NOISE}.gaussian_noise_perturber",
                "PepperNoisePerturber": f"{_NOISE}.pepper_noise_perturber",
                "SaltAndPepperNoisePerturber": f"{_NOISE}.salt_and_pepper_noise_perturber",
                "SaltNoisePerturber": f"{_NOISE}.salt_noise_perturber",
                "SpeckleNoisePerturber": f"{_NOISE}.speckle_noise_perturber",
            },
            extras=["skimage"],
        ),
    ],
)
