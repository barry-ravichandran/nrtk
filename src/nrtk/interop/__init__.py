"""Define the nrtk.interop package."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.interop._maite.augmentations._maite_image_classification_augmentation import (
        MAITEImageClassificationAugmentation as MAITEImageClassificationAugmentation,
    )
    from nrtk.interop._maite.augmentations._maite_multiobject_tracking_augmentation import (
        MAITEMultiobjectTrackingAugmentation as MAITEMultiobjectTrackingAugmentation,
    )
    from nrtk.interop._maite.augmentations._maite_object_detection_augmentation import (
        MAITEObjectDetectionAugmentation as MAITEObjectDetectionAugmentation,
    )

_AUGMENTATIONS = "nrtk.interop._maite.augmentations"

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "MAITEImageClassificationAugmentation": f"{_AUGMENTATIONS}._maite_image_classification_augmentation",
                "MAITEObjectDetectionAugmentation": f"{_AUGMENTATIONS}._maite_object_detection_augmentation",
            },
            extras=["maite"],
        ),
        # Register this one as an entrypoint when it goes stable.
        Group(
            symbols={
                "MAITEMultiobjectTrackingAugmentation": f"{_AUGMENTATIONS}._maite_multiobject_tracking_augmentation",
            },
            extras=["maite"],
            experimental=True,
        ),
    ],
)
