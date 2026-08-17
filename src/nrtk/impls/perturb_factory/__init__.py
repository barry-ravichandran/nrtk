"""Module for all implementations of PerturbFactory."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nrtk._guard import Group, guard

if TYPE_CHECKING:
    from nrtk.impls.perturb_factory._perturber_linspace_factory import (
        PerturberLinspaceFactory as PerturberLinspaceFactory,
    )
    from nrtk.impls.perturb_factory._perturber_multivariate_factory import (
        PerturberMultivariateFactory as PerturberMultivariateFactory,
    )
    from nrtk.impls.perturb_factory._perturber_one_step_factory import (
        PerturberOneStepFactory as PerturberOneStepFactory,
    )
    from nrtk.impls.perturb_factory._perturber_step_factory import (
        PerturberStepFactory as PerturberStepFactory,
    )

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
__all__: list[str]

__getattr__, __dir__, __all__ = guard(
    namespace=globals(),
    groups=[
        Group(
            symbols={
                "PerturberLinspaceFactory": "nrtk.impls.perturb_factory._perturber_linspace_factory",
                "PerturberMultivariateFactory": "nrtk.impls.perturb_factory._perturber_multivariate_factory",
                "PerturberOneStepFactory": "nrtk.impls.perturb_factory._perturber_one_step_factory",
                "PerturberStepFactory": "nrtk.impls.perturb_factory._perturber_step_factory",
            },
        ),
    ],
)
