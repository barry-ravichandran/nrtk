"""Module for optical implementations of :class:`nrtk.interfaces.PerturbVideo`."""

import importlib
from typing import TYPE_CHECKING, Any

from nrtk import _experimental

if TYPE_CHECKING:
    from nrtk.impls.perturb_video.optical._hcipy.turbulence_video_perturber import (
        TurbulenceVideoPerturber as TurbulenceVideoPerturber,
    )

_HCIPY_CLASSES = ["TurbulenceVideoPerturber"]
_EXPERIMENTAL = {
    "TurbulenceVideoPerturber": "nrtk.impls.perturb_video.optical._hcipy.turbulence_video_perturber",
}

__all__: list[str] = []


def _hcipy_extra_error(*, name: str, cause: ImportError | None) -> ImportError:
    msg = f"{name} requires the `hcipy` extra. Install with: `pip install nrtk[hcipy]`"
    if cause is not None:
        msg += (
            "\n\nIf the extra is already installed, the following upstream error may be the cause:"
            f"\n  {type(cause).__name__}: {cause}"
        )
    return ImportError(msg)


def __getattr__(name: str) -> Any:  # noqa: ANN401
    source = _EXPERIMENTAL.get(name)
    if source is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Check the experimental gate before reporting a missing optional extra
    _experimental.require(f"{__name__}.{name}")

    try:
        obj = getattr(importlib.import_module(source), name)
    except ImportError as ex:
        if name in _HCIPY_CLASSES:
            raise _hcipy_extra_error(name=name, cause=ex) from ex
        raise

    obj.__module__ = __name__
    globals()[name] = obj
    return obj
