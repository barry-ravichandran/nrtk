"""Private API for MAITE augmentation wrappers."""

from __future__ import annotations

from nrtk import _experimental

__all__ = [
    "MAITEImageClassificationAugmentation",
    "MAITEObjectDetectionAugmentation",
]


from nrtk.interop._maite.augmentations._maite_image_classification_augmentation import (
    MAITEImageClassificationAugmentation as MAITEImageClassificationAugmentation,
)
from nrtk.interop._maite.augmentations._maite_object_detection_augmentation import (
    MAITEObjectDetectionAugmentation as MAITEObjectDetectionAugmentation,
)

if _experimental.enabled:
    from nrtk.interop._maite.augmentations._maite_multiobject_tracking_augmentation import (
        MAITEMultiobjectTrackingAugmentation as MAITEMultiobjectTrackingAugmentation,
    )

    __all__ += ["MAITEMultiobjectTrackingAugmentation"]
