"""Defines a factory to create perturber instances for flexible image perturbations.

PerturberMultivariateFactory: A base factory class that generates multiple pertuber instances
with specified perturbation parameters.

Example:
    >>> from nrtk.impls.perturb_image.photometric.enhance import BrightnessPerturber
    >>> factory = PerturberMultivariateFactory(
    ...     perturber=BrightnessPerturber, theta_keys=["factor"], thetas=[[0.1, 0.5]]
    ... )
"""

__all__ = ["PerturberMultivariateFactory"]

from collections.abc import Iterable, Iterator, Sequence
from copy import deepcopy
from typing import Any, Generic

from typing_extensions import deprecated, override

from nrtk.interfaces import PerturbFactory
from nrtk.interfaces._perturb_factory import PerturbT_co


class PerturberMultivariateFactory(PerturbFactory[PerturbT_co], Generic[PerturbT_co]):
    """Base factory for creating perturber instances with customizable parameters.

    This factory generates multiple perturber instances, each configured with a unique combination
    of specified perturbation parameters (`theta_keys` and `thetas`). These instances allow for flexible
    image perturbation.

    Attributes:
        perturber (type[PerturbT_co]):
            Type of the perturber to produce.

            .. deprecated:: 1.1
                Use get_config() instead.
        theta_keys (Iterable[str]):
            Names of parameters to vary across instances.

            .. deprecated:: 1.1
                Use get_config() instead.
        sets (Sequence[list[int]]):
            Index combinations for each parameter variation.

            .. deprecated:: 1.1
                This property will be removed in a future major release.
    """

    @staticmethod
    def _build_set_list(*, layer: int, top: Sequence[int]) -> Sequence[list[int]]:
        """Recursively builds a list of index sets to access combinations of parameter values.

        Args:
            layer (int): Current depth of recursion.
            top (Sequence[int]): Maximum index values for each parameter.

        Returns:
            Sequence[list[int]]: A list of index combinations to access parameter values.
        """
        if layer == len(top) - 1:
            return [[i] for i in range(top[layer])]

        return [
            [i] + e
            for i in range(top[layer])
            for e in PerturberMultivariateFactory._build_set_list(layer=layer + 1, top=top)
        ]

    def __init__(
        self,
        *,
        perturber: type[PerturbT_co],
        theta_keys: Iterable[str],
        thetas: Sequence[Any],
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initializes the PerturberMultivariateFactory.

        Args:
            perturber:
                Python implementation type of the perturber to produce.
            theta_keys:
                Names of perturbation parameters to vary
            thetas:
                Values to use for each perturbation parameter.
            perturber_kwargs:
                Default kwargs to be used by the perturber. Defaults to {}.

        Raises:
            TypeError:
                If perturber is an instance instead of a type.
            ValueError:
                If theta_keys is empty or theta_keys and thetas have different lengths.
        """
        # Validate perturber is a type, not an instance
        if not isinstance(perturber, type):
            raise TypeError("Passed a perturber instance, expected type")

        self._perturber = perturber
        self._thetas = thetas  # Must be initialized before theta_keys
        self._theta_keys = self._validate_theta_keys(theta_keys)

        top = [len(entry) for entry in self._thetas]
        self._sets: Sequence[list[int]] = PerturberMultivariateFactory._build_set_list(layer=0, top=top)
        self._n: int = 0
        self._perturber_kwargs: dict[str, Any] = {} if perturber_kwargs is None else perturber_kwargs

    @override
    def __len__(self) -> int:
        """Returns the number of possible perturbation instances."""
        return len(self._sets)

    @override
    def __iter__(self) -> Iterator[PerturbT_co]:
        """Resets the iterator and returns itself for use in for-loops."""
        self._n = 0
        return self

    @override
    def __next__(self) -> PerturbT_co:
        """Returns the next perturber instance with a unique parameter configuration.

        Raises:
            StopIteration:
                When all configurations have been iterated over.
        """
        if self._n < len(self._sets):
            kwargs = {k: self._thetas[i][self._sets[self._n][i]] for i, k in enumerate(self._theta_keys)}
            func = self._create_perturber(kwargs=kwargs)
            self._n += 1
            return func
        raise StopIteration

    @override
    def __getitem__(self, idx: int) -> PerturbT_co:
        """Retrieves a specific perturber instance by index.

        Args:
            idx: Index of the desired perturbation configuration (supports negative indices).

        Returns:
            PerturbT_co: The configured perturb instance.
        """
        kwargs = {k: self._thetas[i][self._sets[idx][i]] for i, k in enumerate(self._theta_keys)}
        return self._create_perturber(kwargs=kwargs)

    @property
    @override
    def thetas(self) -> Sequence[Sequence[Any]]:
        """Returns the current values for each parameter to be varied."""
        return self._thetas

    @property
    @override
    @deprecated(
        "This property will be removed in a future major release.",
    )
    def theta_key(self) -> str:
        """Returns the parameter key associated with the perturbation settings.

        Returns:
            str: The parameter key name, "params".
        """
        return "params"

    @property
    @deprecated(
        "Use get_config() instead.",
    )
    def theta_keys(self) -> Iterable[str]:
        return list(self._theta_keys)

    def _validate_theta_keys(self, theta_keys: Iterable[str]) -> Iterable[str]:
        # Convert theta_keys to list to allow len() and reuse
        theta_keys_list = list(theta_keys)

        # Validate theta_keys is not empty
        if len(theta_keys_list) == 0:
            raise ValueError("theta_keys must not be empty; at least one parameter key is required")

        # Validate theta_keys and thetas have same length
        if len(theta_keys_list) != len(self._thetas):
            raise ValueError(
                f"theta_keys and thetas must have the same length; "
                f"got {len(theta_keys_list)} keys and {len(self._thetas)} theta sequences",
            )

        return theta_keys_list

    @theta_keys.setter
    @deprecated(
        "Setting this property will be removed in a future major release.",
    )
    def theta_keys(self, theta_keys: Iterable[str]) -> None:
        self._theta_keys = self._validate_theta_keys(theta_keys)

    @property
    @deprecated(
        "This property will be removed in a future major release.",
    )
    def sets(self) -> Sequence[list[int]]:
        return deepcopy(self._sets)

    @sets.setter
    @deprecated(
        "This property will be removed in a future major release.",
    )
    def sets(self, sets: Sequence[list[int]]) -> None:
        self._sets = deepcopy(sets)

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the `PerturberMultivariateFactory` instance."""
        return {
            "perturber": self._perturber.get_type_string(),
            "theta_keys": list(self._theta_keys),
            "thetas": deepcopy(self._thetas),
            "perturber_kwargs": deepcopy(self._perturber_kwargs),
        }
