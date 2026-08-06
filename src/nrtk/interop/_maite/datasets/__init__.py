"""Internal MAITE dataset wrappers. Not part of the public API."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.interop._maite.datasets._coco_maite_object_detection_dataset import (
        COCOMAITEObjectDetectionDataset as COCOMAITEObjectDetectionDataset,
    )
    from nrtk.interop._maite.datasets._coco_maite_object_detection_dataset import (
        dataset_to_coco as dataset_to_coco,
    )
    from nrtk.interop._maite.datasets._maite_image_classification_dataset import (
        MAITEImageClassificationDataset as MAITEImageClassificationDataset,
    )
    from nrtk.interop._maite.datasets._maite_object_detection_dataset import (
        MAITEObjectDetectionDataset as MAITEObjectDetectionDataset,
    )
    from nrtk.interop._maite.datasets._maite_object_detection_dataset import (
        MAITEObjectDetectionTarget as MAITEObjectDetectionTarget,
    )

_DATASETS = "nrtk.interop._maite.datasets"

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "MAITEImageClassificationDataset": f"{_DATASETS}._maite_image_classification_dataset",
                "MAITEObjectDetectionDataset": f"{_DATASETS}._maite_object_detection_dataset",
                "MAITEObjectDetectionTarget": f"{_DATASETS}._maite_object_detection_dataset",
            },
            extras=["maite"],
        ),
        Group(
            symbols={
                "COCOMAITEObjectDetectionDataset": f"{_DATASETS}._coco_maite_object_detection_dataset",
                "dataset_to_coco": f"{_DATASETS}._coco_maite_object_detection_dataset",
            },
            extras=["maite", "tools"],
        ),
    ],
)
