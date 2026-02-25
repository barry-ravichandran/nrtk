"""Module for all PerturbImage implementations."""

from typing import Any

import lazy_loader as lazy

from nrtk.impls.perturb_image._compose_perturber import ComposePerturber

# Override __module__ to reflect the public API path for plugin discovery
ComposePerturber.__module__ = __name__

_lazy_getattr, _lazy_dir, _lazy_all = lazy.attach(
    __name__,
    submodules=["geometric", "photometric", "environment", "optical", "generative"],
)

__all__: list[str] = list(_lazy_all) + ["ComposePerturber"]

# Albumentations-based perturbers (optional)
_ALBUMENTATIONS_CLASSES = ["AlbumentationsPerturber"]

_import_error: ImportError | None = None

try:
    from nrtk.impls.perturb_image._albumentations.albumentations_perturber import (
        AlbumentationsPerturber as AlbumentationsPerturber,
    )

    AlbumentationsPerturber.__module__ = __name__

    __all__ += _ALBUMENTATIONS_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> Any:  # noqa: ANN401 - module-level __getattr__ must return Any
    if name in _ALBUMENTATIONS_CLASSES:
        msg = (
            f"{name} requires the `albumentations` and (`graphics` or `headless`) extras. "
            f"Install with: `pip install nrtk[albumentations,graphics]` or `pip install nrtk[albumentations,headless]`"
        )
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    return _lazy_getattr(name)


def __dir__() -> list[str]:
    return __all__
