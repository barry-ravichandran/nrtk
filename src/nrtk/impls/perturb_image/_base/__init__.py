"""Private base classes for perturb_image implementations."""

from nrtk.impls.perturb_image._base._numpy_random_perturb_image import NumpyRandomPerturbImage

__all__ = ["NumpyRandomPerturbImage"]

_TORCH_CLASSES = ["TorchRandomPerturbImage"]

_import_error: ImportError | None = None

try:
    from nrtk.impls.perturb_image._base._torch_random_perturb_image import (
        TorchRandomPerturbImage as TorchRandomPerturbImage,
    )

    __all__ += _TORCH_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _TORCH_CLASSES:
        msg = f"{name} requires torch. Install with: `pip install nrtk[diffusion]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
