"""Defines PerturberLinspaceFactory to create PerturbImage instances with parameters linearly spaced over a range.

Classes:
    PerturberLinspaceFactory: A factory class for creating `PerturbImage` instances
    where a specified parameter varies over a defined range in linearly spaced steps.

Dependencies:
    - numpy for generating linearly spaced values.
    - nrtk.interfaces for the `PerturbImage` and `PerturbImageFactory` interfaces.

Usage:
    To use `PerturberLinspaceFactory`, initialize it with a `PerturbImage` type, a `theta_key`
    to vary, and specify the start, stop, and number of samples. This factory can then be used to
    generate perturbed image instances with linearly spaced parameter variations.

Example:
    >>> from nrtk.impls.perturb_image.photometric.enhance import BrightnessPerturber
    >>> factory = PerturberLinspaceFactory(
    ...     perturber=BrightnessPerturber, theta_key="factor", start=0.0, stop=1.0, num=5
    ... )
"""

from __future__ import annotations

__all__ = ["PerturberLinspaceFactory"]

from collections.abc import Sequence
from typing import Any

from typing_extensions import deprecated, override

from nrtk.impls.perturb_factory._perturber_linspace_factory import (
    PerturberLinspaceFactory as GenericLinspaceFactory,
)
from nrtk.interfaces import PerturbImage, PerturbImageFactory


@deprecated("Use nrtk.impls.perturb_factory.PerturberLinspaceFactory instead.")
class PerturberLinspaceFactory(PerturbImageFactory):
    """Deprecated PerturbImageFactory implementation to iterate over the given linspace.

    .. deprecated:: 1.1
        Use :class:`nrtk.impls.perturb_factory.PerturberLinspaceFactory` instead.
        :mod:`nrtk.impls.perturb_image_factory` will be removed in a future major release.

    Attributes:
        perturber (type[PerturbImage]):
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
            end value of range

            .. deprecated:: 1.1
                Use get_config() instead.
        num (int):
            number of values between start and stop

            .. deprecated:: 1.1
                Use get_config() instead.
        endpoint (bool):
            whether linspace includes stop

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
        num: int = 1,
        endpoint: bool = True,
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the factory to produce PerturbImage instances of the given type.

        Initialize the factory to produce PerturbImage instances of the given type,
        varying the given ``theta_key`` parameter from start to stop with given num.

        Args:
            perturber:
                Python implementation type of the PerturbImage interface to produce.
            theta_key:
                Perturber parameter to vary between instances.
            start:
                Initial value of desired range (inclusive).
            stop:
                End value of desired range.
            num:
                Number of instances to generate.
            endpoint:
                Whether linspace includes stop.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                Given a perturber instance instead of type.
        """
        super().__init__(perturber=perturber, theta_key=theta_key, perturber_kwargs=perturber_kwargs)

        self._new_impl = GenericLinspaceFactory(
            perturber=perturber,
            theta_key=theta_key,
            start=start,
            stop=stop,
            num=num,
            endpoint=endpoint,
            perturber_kwargs=perturber_kwargs,
        )

    @property
    @override
    def thetas(self) -> Sequence[float]:
        """Use linspace to generate the desired range of values."""
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
    def num(self) -> int:
        return self._new_impl.num

    @num.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def num(self, num: int) -> None:
        self._new_impl.num = num

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def endpoint(self) -> bool:
        return self._new_impl.endpoint

    @endpoint.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def endpoint(self, endpoint: bool) -> None:
        self._new_impl.endpoint = endpoint

    @override
    def get_config(self) -> dict[str, Any]:
        return self._new_impl.get_config()
