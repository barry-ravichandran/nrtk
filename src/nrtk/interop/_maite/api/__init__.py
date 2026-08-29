"""Internal MAITE API handlers. Not part of the public API."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.interop._maite.api._app import handle_post as handle_post
    from nrtk.interop._maite.api._aukus_app import handle_aukus_post as handle_aukus_post

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "handle_post": "nrtk.interop._maite.api._app",
                "handle_aukus_post": "nrtk.interop._maite.api._aukus_app",
            },
            extras=["maite", "tools"],
        ),
    ],
)
