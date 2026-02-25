"""Public API for MAITE API handlers.

This module provides import guards for optional dependencies:
- handle_post, handle_aukus_post: require ``maite`` and ``tools`` extras
"""

from __future__ import annotations

_MAITE_TOOLS_CLASSES = ["handle_post", "handle_aukus_post"]

__all__: list[str] = []

_import_error: ImportError | None = None

try:
    from nrtk.interop._maite.api._app import handle_post as handle_post
    from nrtk.interop._maite.api._aukus_app import handle_aukus_post as handle_aukus_post

    __all__ += _MAITE_TOOLS_CLASSES
except ImportError as _ex:
    _import_error = _ex


def __getattr__(name: str) -> None:
    if name in _MAITE_TOOLS_CLASSES:
        msg = f"{name} requires the `maite` and `tools` extras. Install with: `pip install nrtk[maite,tools]`"
        if _import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_import_error).__name__}: {_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
