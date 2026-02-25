"""Public API for MAITE augmentation wrappers.

This module provides import guards for optional dependencies:
- MAITEImageClassificationAugmentation, MAITEObjectDetectionAugmentation:
  require ``maite`` extra
"""

from __future__ import annotations

_MAITE_CLASSES = [
    "MAITEImageClassificationAugmentation",
    "MAITEObjectDetectionAugmentation",
]

__all__: list[str] = []

_import_error: ImportError | None = None

try:
    from nrtk.interop._maite.augmentations._maite_image_classification_augmentation import (
        MAITEImageClassificationAugmentation as MAITEImageClassificationAugmentation,
    )
    from nrtk.interop._maite.augmentations._maite_object_detection_augmentation import (
        MAITEObjectDetectionAugmentation as MAITEObjectDetectionAugmentation,
    )

    __all__ += _MAITE_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _MAITE_CLASSES:
        msg = f"{name} requires the `maite` extra. Install with: `pip install nrtk[maite]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
