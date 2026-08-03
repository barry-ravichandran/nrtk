"""Module for photometric implementations of PerturbImage."""

from collections.abc import Callable
from typing import Any

from nrtk._guard import guard

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    submodules=[
        "blur",
        "enhance",
        "noise",
    ],
)
