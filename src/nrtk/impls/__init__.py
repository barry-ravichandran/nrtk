"""Module for all implementations of nrtk interfaces.

``perturb_video`` is deliberately absent: everything in it is experimental, and a
parent package must not advertise more than its children are willing to expose.
"""

from collections.abc import Callable
from typing import Any

from nrtk._guard import guard

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    submodules=[
        "perturb_image",
        "perturb_image_factory",  # Deprecated, but kept for compatibility
        "perturb_factory",
    ],
)
