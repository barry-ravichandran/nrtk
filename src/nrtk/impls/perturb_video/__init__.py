"""Module for all PerturbVideo implementations."""

import importlib
from typing import TYPE_CHECKING, Any

import lazy_loader as lazy

from nrtk import _experimental

if TYPE_CHECKING:
    # Real types for the gated experimental interfaces below. Skipped at runtime, so
    # the __getattr__ gate still controls actual access; this only lets type checkers
    # see the upstream classes (so subclasses resolve base methods and @override).
    from nrtk.impls.perturb_video._framewise_perturber import FramewisePerturber as FramewisePerturber

_lazy_getattr, _lazy_dir, _lazy_all = lazy.attach(
    __name__,
    submodules=["optical"],
)

__all__: list[str] = list(_lazy_all)

# Experimental interfaces are exposed from this stable location but gated behind
# ``import nrtk.experimental`` and kept out of ``__all__``. Each maps to the private
# module that defines it; add an entry to enroll another. Per PEP 562 this hook only
# runs for names normal lookup misses, so the stable exports above never reach it.
_EXPERIMENTAL = {
    "FramewisePerturber": "nrtk.impls.perturb_video._framewise_perturber",
}


def __getattr__(name: str) -> Any:  # noqa: ANN401
    source = _EXPERIMENTAL.get(name)
    if source is not None:
        _experimental.require(f"{__name__}.{name}")
        obj = getattr(importlib.import_module(source), name)
        obj.__module__ = __name__
        globals()[name] = obj  # cache so later lookups skip this hook
        return obj
    return _lazy_getattr(name)


def __dir__() -> list[str]:
    return __all__
