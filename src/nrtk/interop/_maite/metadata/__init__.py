"""Public API for MAITE datum-level metadata definitions.

This module provides import guards for optional dependencies:
- NRTKDatumMetadata: requires ``maite`` extra
"""

from __future__ import annotations

_MAITE_CLASSES = [
    "NRTKDatumMetadata",
]

__all__: list[str] = []

_import_error: ImportError | None = None

try:
    from nrtk.interop._maite.metadata._nrtk_datum_metadata import (
        NRTKDatumMetadata as NRTKDatumMetadata,
    )

    __all__ += _MAITE_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _MAITE_CLASSES:
        msg = f"{name} requires the `maite` extra. Install with: `pip install nrtk[maite]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
