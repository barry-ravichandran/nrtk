"""Deprecated PerturbImageFactory, an abstract factory for creating configurable PerturbImage instances flexibly.

Classes:
    PerturbImageFactory: An abstract factory for creating `PerturbImage` instances with specific
    configurations. Allows for custom parameterization of generated instances.

Dependencies:
    - smqtk_core.Plugfigurable for plug-and-play configuration support.
    - nrtk.interfaces.PerturbImage as the base interface for perturbing images.

Example usage:
    factory = PerturbImageFactory(perturber=SomePerturbImageClass, theta_key="altitude")
    for perturber in factory:
        perturber(image=perturbed_image)
"""

from __future__ import annotations

__all__ = ["PerturbImageFactory"]

from typing import Any

from typing_extensions import deprecated

from nrtk.interfaces._perturb_factory import PerturbFactory
from nrtk.interfaces._perturb_image import PerturbImage


@deprecated("Use nrtk.interfaces.PerturbFactory instead.")
class PerturbImageFactory(PerturbFactory[PerturbImage]):
    """Factory class for producing PerturbImage instances of a specified type and configuration.

    .. deprecated:: 1.1
        Use :class:`nrtk.interfaces.PerturbFactory` instead.
        :class:`nrtk.interfaces.PerturbImageFactory` will be removed in a future major release.

    Attributes:
        .. deprecated:: 1.1
            Use get_config() instead.
        theta_key (str): perturber parameter to vary between instances

        .. deprecated:: 1.1
            Use get_config() instead.
    """

    def __init__(
        self,
        *,
        perturber: type[PerturbImage],
        theta_key: str,
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the factory to produce PerturbImage instances of the given type.

        Initialize the factory to produce PerturbImage instances of the given type,
        varying the given `theta_key` parameter.

        Args:
            perturber:
                Python implementation type of the PerturbImage interface to produce.
            theta_key:
                Perturber parameter to vary between instances.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                Given a perturber instance instead of type.
        """
        super().__init__(perturber=perturber, theta_key=theta_key, perturber_kwargs=perturber_kwargs)
