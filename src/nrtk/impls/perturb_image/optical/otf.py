"""pyBSM OTF perturber implementations."""

_OTF_CLASSES = [
    "CircularAperturePerturber",
    "DefocusPerturber",
    "DetectorPerturber",
    "JitterPerturber",
    "TurbulenceAperturePerturber",
]

_PYBSM_FUNCTIONS = [
    "load_default_config",
]

__all__: list[str] = []

_import_error: ImportError | None = None

try:
    from nrtk.impls.perturb_image.optical._pybsm import (
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

    # Override __module__ to reflect the public API path for plugin discovery
    CircularAperturePerturber.__module__ = __name__
    DefocusPerturber.__module__ = __name__
    DetectorPerturber.__module__ = __name__
    JitterPerturber.__module__ = __name__
    TurbulenceAperturePerturber.__module__ = __name__

    __all__ += _PYBSM_FUNCTIONS + _OTF_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _OTF_CLASSES or name in _PYBSM_FUNCTIONS:
        msg = f"{name} requires the `pybsm` extra. Install with: `pip install nrtk[pybsm]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
