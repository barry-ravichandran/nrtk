"""Public API for MAITE dataset wrappers.

This module provides import guards for optional dependencies:
- MAITEImageClassificationDataset, MAITEObjectDetectionDataset, MAITEObjectDetectionTarget:
  require ``maite`` extra
- COCOMAITEObjectDetectionDataset, dataset_to_coco: require ``maite`` and ``tools`` extras
"""

from __future__ import annotations

# Maite-only classes (require maite extra)
_MAITE_CLASSES = [
    "MAITEImageClassificationDataset",
    "MAITEObjectDetectionDataset",
    "MAITEObjectDetectionTarget",
]

# kwcoco/Pillow-dependent classes (require tools extra)
_MAITE_TOOLS_CLASSES = ["COCOMAITEObjectDetectionDataset", "dataset_to_coco"]

__all__: list[str] = []

_maite_import_error: ImportError | None = None
_tools_import_error: ImportError | None = None

try:
    from nrtk.interop._maite.datasets._maite_image_classification_dataset import (
        MAITEImageClassificationDataset as MAITEImageClassificationDataset,
    )
    from nrtk.interop._maite.datasets._maite_object_detection_dataset import (
        MAITEObjectDetectionDataset as MAITEObjectDetectionDataset,
    )
    from nrtk.interop._maite.datasets._maite_object_detection_dataset import (
        MAITEObjectDetectionTarget as MAITEObjectDetectionTarget,
    )

    __all__ += _MAITE_CLASSES
except ImportError as _ex:
    _maite_import_error = _ex


try:
    from nrtk.interop._maite.datasets._coco_maite_object_detection_dataset import (
        COCOMAITEObjectDetectionDataset as COCOMAITEObjectDetectionDataset,
    )
    from nrtk.interop._maite.datasets._coco_maite_object_detection_dataset import (
        dataset_to_coco as dataset_to_coco,
    )

    __all__ += _MAITE_TOOLS_CLASSES
except ImportError as _ex:
    _tools_import_error = _ex


def __getattr__(name: str) -> None:
    if name in _MAITE_CLASSES:
        msg = f"{name} requires the `maite` extra. Install with: `pip install nrtk[maite]`"
        if _maite_import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_maite_import_error).__name__}: {_maite_import_error}"
            )
        raise ImportError(msg)
    if name in _MAITE_TOOLS_CLASSES:
        msg = f"{name} requires the `maite` and `tools` extras. Install with: `pip install nrtk[maite,tools]`"
        if _tools_import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_tools_import_error).__name__}: {_tools_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
