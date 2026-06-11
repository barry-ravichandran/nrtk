"""Runtime state for NRTK's experimental features.

A tiny flag module that imports nothing from nrtk, so anything can read
``enabled`` without risking an import cycle. Importing :mod:`nrtk.experimental`
flips it on.
"""

import warnings


class ExperimentalWarning(UserWarning):
    """Emitted the first time an experimental symbol is used."""


enabled: bool = False
_warned: set[str] = set()


def require(name: str) -> None:
    """Raise unless experimental features are enabled; warn once per symbol when they are.

    Args:
        name: Fully qualified symbol name, used in the message.

    Raises:
        ImportError: If experimental features are not enabled.
    """
    if not enabled:
        raise ImportError(
            f"{name} is experimental. Enable it with `import nrtk.experimental` before importing it. "
            "Experimental APIs may change without a deprecation warning.",
        )
    if name not in _warned:
        _warned.add(name)
        warnings.warn(
            message=f"{name} is experimental; its API may change without a deprecation warning.",
            category=ExperimentalWarning,
            stacklevel=2,
        )


# Adding an experimental implementation
# -------------------------------------
# An experimental impl uses the usual optional-dependency ("extras") module pattern,
# with two additions: only expose the classes when experimental is enabled, and call
# `require()` first in `__getattr__`. For example, in the impl's public module
# (e.g. nrtk/impls/perturb_image/photometric/blur.py):
#
#     from nrtk import _experimental
#
#     _CLASSES = ["FooPerturber"]
#     __all__: list[str] = []
#     _import_error: ImportError | None = None
#
#     if _experimental.enabled:                        # 1. experimental gate
#         try:
#             from nrtk.impls.<...>._foo import FooPerturber as FooPerturber
#             FooPerturber.__module__ = __name__
#             __all__ += _CLASSES
#         except ImportError as _ex:                   # extra gate (the existing extras pattern)
#             _import_error = _ex
#
#     def __getattr__(name: str):
#         if name not in _CLASSES:
#             raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
#         _experimental.require(f"{__name__}.{name}")  # 2. experimental gate, first
#         msg = f"{name} requires the `<extra>` extra. Install with `pip install nrtk[<extra>]`."
#         if _import_error is not None:
#             msg += f"\n  upstream cause: {type(_import_error).__name__}: {_import_error}"
#         raise ImportError(msg)
#
# When experimental is on and the extra is installed the classes are real module
# attributes, so plugin discovery and config find them like any other perturber. A
# core-only experimental impl is the same without the try/except, just the
# `if _experimental.enabled:` guard.
