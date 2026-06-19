"""Define the nrtk.interop package."""

from __future__ import annotations

import importlib
from typing import Any

from nrtk import _experimental

_MAITE_CLASSES = [
    "MAITEImageClassificationAugmentation",
    "MAITEObjectDetectionAugmentation",
    "MAITEMultiobjectTrackingAugmentation",
]

# Experimental classes load lazily on access, gated behind `import nrtk.experimental`.
# Map to the *leaf* module, not the augmentations package (which has its own gate),
# so access is import-order independent. Register as an entrypoint when it goes stable.
_EXPERIMENTAL = {
    "MAITEMultiobjectTrackingAugmentation": "nrtk.interop._maite.augmentations._maite_multiobject_tracking_augmentation",  # noqa: E501 (line too long + dict format incompatibility)
}

__all__: list[str] = []

_import_error: ImportError | None = None
try:
    from nrtk.interop._maite.augmentations import (
        MAITEImageClassificationAugmentation as MAITEImageClassificationAugmentation,
    )
    from nrtk.interop._maite.augmentations import (
        MAITEObjectDetectionAugmentation as MAITEObjectDetectionAugmentation,
    )

    MAITEImageClassificationAugmentation.__module__ = __name__
    MAITEObjectDetectionAugmentation.__module__ = __name__

    __all__ += [maite_cls for maite_cls in _MAITE_CLASSES if maite_cls not in _EXPERIMENTAL]
except ImportError as _ex:
    _import_error = _ex


def _maite_extra_error(*, name: str, cause: ImportError | None) -> ImportError:
    msg = f"{name} requires the `maite` extra. Install with: `pip install nrtk[maite]`"
    if cause is not None:
        msg += (
            "\n\nIf the extra is already installed, the following upstream error may be the cause:"
            f"\n  {type(cause).__name__}: {cause}"
        )
    return ImportError(msg)


def __getattr__(name: str) -> Any:  # noqa: ANN401
    source = _EXPERIMENTAL.get(name)
    if source is not None:  # experimental class
        _experimental.require(f"{__name__}.{name}")  # gate 1: experimental (first)
        try:
            obj = getattr(importlib.import_module(source), name)  # gate 2: extra-based gates
        except ImportError as ex:
            if name in _MAITE_CLASSES:
                raise _maite_extra_error(name=name, cause=ex) from ex
            raise ex
        obj.__module__ = __name__
        globals()[name] = obj  # cache so later lookups skip this hook
        return obj

    if name in _MAITE_CLASSES:  # stable classes, behind the maite extra
        raise _maite_extra_error(name=name, cause=_import_error)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
