"""Defines PerturberOneStepFactory, creating a single PerturbImage with fixed parameters for one-step perturbations.

Classes:
    PerturberOneStepFactory: A factory that generates one `PerturbImage` instance
    configured with a specific parameter key and value.

Dependencies:
    - nrtk.impls.perturb_image_factory.PerturberStepFactory for the base
      factory functionality.
    - nrtk.interfaces.PerturbImage as the interface for the perturber.

Example usage:
    >>> from nrtk.impls.perturb_image.photometric.enhance import BrightnessPerturber
    >>> factory = PerturberOneStepFactory(perturber=BrightnessPerturber, theta_key="factor", theta_value=0.5)
"""

__all__ = ["PerturberOneStepFactory"]

from typing import Any

from typing_extensions import deprecated, override

from nrtk.impls.perturb_factory._perturber_one_step_factory import (
    PerturberOneStepFactory as GenericOneStepFactory,
)
from nrtk.impls.perturb_image_factory._perturber_step_factory import (
    PerturberStepFactory,
)
from nrtk.interfaces import PerturbImage


@deprecated("Use nrtk.impls.perturb_factory.PerturberOneStepFactory instead.")
class PerturberOneStepFactory(PerturberStepFactory):
    """Deprecated PerturbImageFactory implementation to return a factory with one perturber.

    .. deprecated:: 1.1
        Use :class:`nrtk.impls.perturb_factory.PerturberOneStepFactory` instead.
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
        theta_value (float):
            value to set theta_key to

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
        theta_value: float,
        to_int: bool = False,
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the factory to produce an instance of PerturbImage for the given type.

        Initialize the factory to produce an instance of PerturbImage for the given type,
        given the ``theta_key`` and the ``theta_value`` parameters.

        Args:
            perturber:
                Python implementation type of the PerturbImage interface to produce.
            theta_key:
                Perturber parameter to vary between instances.
            theta_value:
                Initial and only value of ``theta_key``.
            to_int:
                Boolean variable determining whether the theta is cast as int or float. Defaults to False.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                Given a perturber instance instead of type.
        """
        super().__init__(
            perturber=perturber,
            theta_key=theta_key,
            start=theta_value,
            stop=theta_value + 0.1,
            step=1.0,
            to_int=to_int,
            perturber_kwargs=perturber_kwargs,
        )

        self._new_impl = GenericOneStepFactory(
            perturber=perturber,
            theta_key=theta_key,
            theta_value=theta_value,
            to_int=to_int,
            perturber_kwargs=perturber_kwargs,
        )

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def theta_value(self) -> float:
        return self._new_impl.theta_value

    @theta_value.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def theta_value(self, theta_value: float) -> None:
        self._new_impl.theta_value = theta_value

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns a configuration dictionary for the PerturberOneStepFactory instance."""
        return self._new_impl.get_config()
