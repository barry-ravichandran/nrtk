"""Package housing the interfaces of nrtk."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.interfaces._perturb_image import PerturbImage as PerturbImage
    from nrtk.interfaces._perturb_image_factory import PerturbImageFactory as PerturbImageFactory
    from nrtk.interfaces._perturb_video import PerturbVideo as PerturbVideo
    from nrtk.interfaces._perturb_video import VideoFrame as VideoFrame

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "PerturbImage": "nrtk.interfaces._perturb_image",
                "PerturbImageFactory": "nrtk.interfaces._perturb_image_factory",
            },
        ),
        Group(
            symbols={
                "PerturbVideo": "nrtk.interfaces._perturb_video",
                "VideoFrame": "nrtk.interfaces._perturb_video",
            },
            experimental=True,
        ),
    ],
)
