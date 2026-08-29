"""Define the nrtk package."""

from collections.abc import Callable
from importlib import metadata
from typing import Any

from nrtk._guard import guard

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__version__ = metadata.version("nrtk")

# ``nrtk._guard`` imports ``nrtk._experimental`` back out of this partially
# initialised package. That resolves through the normal submodule import, and
# ``_experimental`` deliberately imports nothing from ``nrtk``, so there is no cycle.
__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    submodules=["entrypoints", "experimental", "impls", "interfaces", "interop", "utils"],
)
