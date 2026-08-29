"""Defines PerturberStepFactory, which creates PerturbImage instances varying a parameter over a range in steps.

Classes:
    PerturberStepFactory: Factory for producing `PerturbImage` instances with a specific
    parameter (`theta_key`) varying over a specified range.

Dependencies:
    - math for range calculations.
    - nrtk.interfaces for the `PerturbImage` and `PerturbImageFactory` interfaces.

Usage:
    Instantiate `PerturberStepFactory` with a `PerturbImage` type, a `theta_key` to vary,
    and the start, stop, and step values for the parameter range. This factory can then be
    used to generate perturbed image instances with controlled variations.

Example:
    >>> from nrtk.impls.perturb_image.photometric.enhance import BrightnessPerturber
    >>> factory = PerturberStepFactory(
    ...     perturber=BrightnessPerturber, theta_key="factor", start=0.0, stop=1.0, step=0.1, to_int=False
    ... )
"""

from __future__ import annotations

__all__ = ["PerturberStepFactory"]

from collections.abc import Sequence
from typing import Any

from typing_extensions import deprecated, override

from nrtk.impls.perturb_factory._perturber_step_factory import (
    PerturberStepFactory as GenericStepFactory,
)
from nrtk.interfaces import PerturbImage, PerturbImageFactory


@deprecated("Use nrtk.impls.perturb_factory.PerturberStepFactory instead.")
class PerturberStepFactory(PerturbImageFactory):
    """Deprecated PerturbImageFactory implementation to step through the given range of values.

    .. deprecated:: 1.1
        Use :class:`nrtk.impls.perturb_factory.PerturberStepFactory` instead.
        :mod:`nrtk.impls.perturb_image_factory` will be removed in a future major release.

    Attributes:
        perturber (type[PerturbT_co]):
            perturber type to produce

            .. deprecated:: 1.1
                Use get_config() instead.
        theta_key (str):
            peturber parameter to modify

            .. deprecated:: 1.1
                Use get_config() instead.
        start (float):
            initial value of range (inclusive)

            .. deprecated:: 1.1
                Use get_config() instead.
        stop (float):
            end value of range (exclusive)

            .. deprecated:: 1.1
                Use get_config() instead.
        step (float):
            step value between instances

            .. deprecated:: 1.1
                Use get_config() instead.
        to_int (bool):
            determines wheter to cast theta_value to a int or float

            .. deprecated:: 1.1
                Use get_config() instead.
    """

    def __init__(
        self,
        *,
        perturber: type[PerturbImage],
        theta_key: str,
        start: float,
        stop: float,
        step: float = 1.0,
        to_int: bool = False,
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the factory to produce PerturbImage instances of the given type.

        Initialize the factory to produce PerturbImage instances of the given type,
        varying the given ``theta_key`` parameter from start to stop with given step.

        Args:
            perturber:
                Python implementation type of the PerturbImage interface to produce.
            theta_key:
                Perturber parameter to vary between instances.
            start:
                Initial value of desired range (inclusive).
            stop:
                Final value of desired range (exclusive).
            step:
                Step value between instances.
            to_int:
                Boolean variable determining whether the thetas are cast as ints or floats. Defaults to False.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                Given a perturber instance instead of type.
        """
        super().__init__(perturber=perturber, theta_key=theta_key, perturber_kwargs=perturber_kwargs)

        self._new_impl = GenericStepFactory(
            perturber=perturber,
            theta_key=theta_key,
            start=start,
            stop=stop,
            step=step,
            to_int=to_int,
            perturber_kwargs=perturber_kwargs,
        )

    @property
    @override
    def thetas(self) -> Sequence[float] | Sequence[int]:
        return self._new_impl.thetas

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def start(self) -> float:
        return self._new_impl.start

    @start.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def start(self, start: float) -> None:
        self._new_impl.start = start

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def stop(self) -> float:
        return self._new_impl.stop

    @stop.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def stop(self, stop: float) -> None:
        self._new_impl.stop = stop

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def step(self) -> float:
        return self._new_impl.step

    @step.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def step(self, step: float) -> None:
        self._new_impl.step = step

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def to_int(self) -> bool:
        return self._new_impl.to_int

    @to_int.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def to_int(self, to_int: bool) -> None:
        self._new_impl.to_int = to_int

    @override
    def get_config(self) -> dict[str, Any]:
        return self._new_impl.get_config()
