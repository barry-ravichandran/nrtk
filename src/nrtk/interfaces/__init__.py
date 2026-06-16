"""Package housing the interfaces of nrtk."""

import importlib
from typing import TYPE_CHECKING, Any

from nrtk import _experimental
from nrtk.interfaces._perturb_image import PerturbImage as PerturbImage
from nrtk.interfaces._perturb_image_factory import PerturbImageFactory as PerturbImageFactory

if TYPE_CHECKING:
    # Real types for the gated experimental interfaces below. Skipped at runtime, so
    # the __getattr__ gate still controls actual access; this only lets type checkers
    # see the upstream classes (so subclasses resolve base methods and @override).
    from nrtk.interfaces._perturb_video import PerturbVideo as PerturbVideo
    from nrtk.interfaces._perturb_video import VideoFrame as VideoFrame

__all__ = ["PerturbImage", "PerturbImageFactory"]

PerturbImage.__module__ = __name__
PerturbImageFactory.__module__ = __name__

# Experimental interfaces are exposed from this stable location but gated behind
# ``import nrtk.experimental`` and kept out of ``__all__``. Each maps to the private
# module that defines it; add an entry to enroll another. Per PEP 562 this hook only
# runs for names normal lookup misses, so the stable exports above never reach it.
_EXPERIMENTAL = {
    "PerturbVideo": "nrtk.interfaces._perturb_video",
    "VideoFrame": "nrtk.interfaces._perturb_video",
}


def __getattr__(name: str) -> Any:  # noqa: ANN401
    source = _EXPERIMENTAL.get(name)
    if source is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    _experimental.require(f"{__name__}.{name}")
    obj = getattr(importlib.import_module(source), name)
    obj.__module__ = __name__
    globals()[name] = obj  # cache so later lookups skip this hook
    return obj
