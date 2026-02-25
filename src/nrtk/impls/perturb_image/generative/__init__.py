"""Module for generative implementations of PerturbImage."""

_DIFFUSION_CLASSES = ["DiffusionPerturber"]

__all__: list[str] = []

_import_error: ImportError | None = None

try:
    from nrtk.impls.perturb_image.generative._diffusion_perturber import (
        DiffusionPerturber as DiffusionPerturber,
    )

    # Override __module__ to reflect the public API path for plugin discovery
    DiffusionPerturber.__module__ = __name__

    __all__ += _DIFFUSION_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _DIFFUSION_CLASSES:
        msg = f"{name} requires the `diffusion` extra. Install with: `pip install nrtk[diffusion]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
