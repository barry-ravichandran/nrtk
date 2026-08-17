"""Defines PerturbFactory, an abstract factory for creating configurable perturber instances flexibly.

Classes:
    PerturbFactory: An abstract factory for creating perturb instances with specific
    configurations. Allows for custom parameterization of generated instances.

Dependencies:
    - smqtk_core.Plugfigurable for plug-and-play configuration support.

Example usage:
    factory = PerturbFactory(perturber=SomePerturberClass, theta_key="altitude")
    for perturber in factory:
        perturber(...)
"""

from __future__ import annotations

__all__ = ["PerturbFactory"]

import abc
from collections.abc import Iterator, Sequence
from copy import deepcopy
from typing import Any, Generic, TypeVar

from typing_extensions import Self, deprecated, override

from nrtk.interfaces._perturb_data import PerturbData
from nrtk.interfaces._plugfigurable import Plugfigurable

PerturbT_co = TypeVar("PerturbT_co", bound=PerturbData, covariant=True)


class PerturbFactory(Plugfigurable, Generic[PerturbT_co]):
    """Factory class for producing perturber instances of a specified type and configuration.

    Attributes:
        perturber (type[PerturbT_co]): python implementation type of the perturber interface to produce

        .. deprecated:: 1.1
            Use get_config() instead.
        theta_key (str): perturber parameter to vary between instances

        .. deprecated:: 1.1
            Use get_config() instead.
    """

    def __init__(
        self,
        *,
        perturber: type[PerturbT_co],
        theta_key: str,
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the factory to produce perturber instances of the given type.

        Initialize the factory to produce perturber instances of the given type,
        varying the given `theta_key` parameter.

        Args:
            perturber:
                Python implementation type of the perturber interface to produce.
            theta_key:
                Perturber parameter to vary between instances.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                Given a perturber instance instead of type.
        """
        self._theta_key = theta_key

        if not isinstance(perturber, type):
            raise TypeError("Passed a perturber instance, expected type")
        self._perturber = perturber
        self._n = -1
        self._perturber_kwargs: dict[str, Any] = {} if perturber_kwargs is None else perturber_kwargs

    def _create_perturber(self, kwargs: dict[str, Any]) -> PerturbT_co:
        """Returns perturber implementation with given input args."""
        input_kwargs = self._perturber_kwargs | kwargs
        return self._perturber(**input_kwargs)

    @property
    @abc.abstractmethod
    def thetas(self) -> Sequence[Any]:
        """Get the sequence of theta values this factory will iterate over."""

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def theta_key(self) -> str:
        """Get the perturber parameter to vary between instances."""
        return self._theta_key

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def perturber(self) -> type[PerturbT_co]:
        return self._perturber

    # Note that this setter technically breaks the rules of covariance/contravariance
    # However, we need to add the deprecation notice. This is no more risky than the
    # "public" attribute, so the risk is accepted
    @perturber.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def perturber(self, perturber: type[PerturbT_co]) -> None:  # pyright: ignore [reportGeneralTypeIssues]
        self._perturber = perturber

    def __len__(self) -> int:
        """Return the number of perturber instances this factory will generate."""
        return len(self.thetas)

    def __iter__(self) -> Iterator[PerturbT_co]:
        """Return an iterator for this factory."""
        self._n = 0
        return self

    def __next__(self) -> PerturbT_co:
        """Return the next perturber instance.

        Raises:
            StopIteration:
                Iterator exhausted.
        """
        if self._n < len(self.thetas):
            kwargs = {self._theta_key: self.thetas[self._n]}
            func = self._create_perturber(kwargs=kwargs)
            self._n += 1
            return func
        raise StopIteration

    def __getitem__(self, idx: int) -> PerturbT_co:
        """Get the perturber for a specific index.

        Args:
            idx: Index of desired perturber (supports negative indices).
        """
        kwargs = {self._theta_key: self.thetas[idx]}

        return self._create_perturber(kwargs=kwargs)

    @override
    @classmethod
    def from_config(
        cls,
        config_dict: dict[str, Any],
        merge_default: bool = True,
    ) -> Self:
        """Instantiates a PerturbFactory from a configuration dictionary.

        Args:
            config_dict: Configuration dictionary with parameters for instantiation.
            merge_default: Whether to merge with default configuration. Defaults to True.

        Returns:
            An instance of the PerturbFactory class.
        """
        config_dict = dict(config_dict)

        # Check to see if there is a perturber key and if it is in bad format
        if "perturber" in config_dict:
            perturber_impls = PerturbData.get_impls()

            type_dict = {pert_impl.get_type_string(): pert_impl for pert_impl in perturber_impls}

            if config_dict["perturber"] not in type_dict:
                raise ValueError(
                    f"{config_dict['perturber']} is not a valid perturber.",
                )

            config_dict["perturber"] = type_dict[config_dict["perturber"]]

        return super().from_config(config_dict, merge_default=merge_default)

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns the configuration of the factory instance."""
        return {
            "perturber": self._perturber.get_type_string(),
            "theta_key": self._theta_key,
            "perturber_kwargs": deepcopy(self._perturber_kwargs),
        }
