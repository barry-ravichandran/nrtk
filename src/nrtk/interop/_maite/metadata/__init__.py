"""Internal MAITE datum-level metadata definitions. Not part of the public API."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.interop._maite.metadata._nrtk_datum_metadata import (
        NRTKDatumMetadata as NRTKDatumMetadata,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={"NRTKDatumMetadata": "nrtk.interop._maite.metadata._nrtk_datum_metadata"},
            extras=["maite"],
        ),
    ],
)
