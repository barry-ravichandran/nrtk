"""pyBSM OTF perturber implementations."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_image.optical._pybsm._default_config import (
        load_default_config as load_default_config,
    )
    from nrtk.impls.perturb_image.optical._pybsm.circular_aperture_perturber import (
        CircularAperturePerturber as CircularAperturePerturber,
    )
    from nrtk.impls.perturb_image.optical._pybsm.defocus_perturber import (
        DefocusPerturber as DefocusPerturber,
    )
    from nrtk.impls.perturb_image.optical._pybsm.detector_perturber import (
        DetectorPerturber as DetectorPerturber,
    )
    from nrtk.impls.perturb_image.optical._pybsm.jitter_perturber import (
        JitterPerturber as JitterPerturber,
    )
    from nrtk.impls.perturb_image.optical._pybsm.turbulence_aperture_perturber import (
        TurbulenceAperturePerturber as TurbulenceAperturePerturber,
    )

_PYBSM = "nrtk.impls.perturb_image.optical._pybsm"

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        # Reads JSON into a plain dict, so it needs pybsm neither to import nor to call.
        Group(symbols={"load_default_config": f"{_PYBSM}._default_config"}),
        Group(
            symbols={
                "CircularAperturePerturber": f"{_PYBSM}.circular_aperture_perturber",
                "DefocusPerturber": f"{_PYBSM}.defocus_perturber",
                "DetectorPerturber": f"{_PYBSM}.detector_perturber",
                "JitterPerturber": f"{_PYBSM}.jitter_perturber",
                "TurbulenceAperturePerturber": f"{_PYBSM}.turbulence_aperture_perturber",
            },
            extras=["pybsm"],
        ),
    ],
)
