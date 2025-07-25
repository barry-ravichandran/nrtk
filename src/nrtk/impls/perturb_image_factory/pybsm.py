"""Defines factories to create PybsmPerturber instances for flexible image perturbations.

Classes:
    _PybsmPerturbImageFactory: A base factory class that generates multiple `PybsmPerturber` instances
    with specified perturbation parameters.

    CustomPybsmPerturbImageFactory: A specialized implementation of `_PybsmPerturbImageFactory` with
    preset configurations.

Dependencies:
    - smqtk_core for configuration management.
    - pybsm for pybsm-based perturbation functionalities.
    - nrtk interfaces for image perturbation.

Example usage:
    sensor = PybsmSensor(...)
    scenario = PybsmScenario(...)
    factory = CustomPybsmPerturbImageFactory(sensor=sensor, scenario=scenario,
                                             theta_keys=['key1'], thetas=[[value1, value2]])
    perturber = next(iter(factory))
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from typing import Any

from smqtk_core.configuration import (
    from_config_dict,
    make_default_config,
    to_config_dict,
)
from typing_extensions import override

from nrtk.impls.perturb_image.pybsm.pybsm_perturber import PybsmPerturber
from nrtk.impls.perturb_image.pybsm.scenario import PybsmScenario
from nrtk.impls.perturb_image.pybsm.sensor import PybsmSensor
from nrtk.interfaces.perturb_image import PerturbImage
from nrtk.interfaces.perturb_image_factory import PerturbImageFactory
from nrtk.utils._exceptions import PyBSMImportError


class _PybsmPerturbImageFactory(PerturbImageFactory):
    """Base factory for creating `PybsmPerturber` instances with customizable sensor and scenario parameters.

    This factory generates multiple `PybsmPerturber` instances, each configured with a unique combination
    of specified perturbation parameters (`theta_keys` and `thetas`). These instances allow for flexible
    image perturbation.

    See https://pybsm.readthedocs.io/en/latest/explanation.html for image formation concepts and parameter details.

    Attributes:
        sensor (PybsmSensor): The sensor configuration for perturbation.
        scenario (PybsmScenario): The scenario configuration for perturbation.
        theta_keys (Iterable[str]): Names of parameters to vary across instances.
        _thetas (Sequence[Any]): Values to vary for each parameter in `theta_keys`.
        sets (Sequence[list[int]]): Index combinations for each parameter variation.
    """

    @staticmethod
    def _build_set_list(layer: int, top: Sequence[int]) -> Sequence[list[int]]:
        """Recursively builds a list of index sets to access combinations of parameter values.

        Args:
            layer (int): Current depth of recursion.
            top (Sequence[int]): Maximum index values for each parameter.

        Returns:
            Sequence[list[int]]: A list of index combinations to access parameter values.
        """
        if layer == len(top) - 1:
            return [[i] for i in range(top[layer])]

        return [[i] + e for i in range(top[layer]) for e in _PybsmPerturbImageFactory._build_set_list(layer + 1, top)]

    def __init__(
        self,
        sensor: PybsmSensor,
        scenario: PybsmScenario,
        theta_keys: Iterable[str],
        thetas: Sequence[Any],
    ) -> None:
        """Initializes the PybsmPerturbImageFactory.

        :param sensor: pyBSM sensor object.
        :param scenario: pyBSM scenario object.
        :param theta_keys: Perturber parameter(s) to vary between instances.
        :param theta_keys: Perturber parameter(s) values to vary between instances.

        :raises: ImportError if pyBSM is not found,
        installed via 'nrtk[pybsm-graphics]' or 'nrtk[pybsm-headless]'.
        """
        if not self.is_usable():
            raise PyBSMImportError
        self.sensor = sensor
        self.scenario = scenario
        self.theta_keys = theta_keys
        self._thetas = thetas

        top = [len(entry) for entry in self.thetas]
        self.sets: Sequence[list[int]] = _PybsmPerturbImageFactory._build_set_list(0, top)

    @override
    def __len__(self) -> int:
        """Returns the number of possible perturbation instances.

        Returns:
            int: The total number of perturbation configurations.
        """
        return len(self.sets)

    @override
    def __iter__(self) -> Iterator[PerturbImage]:
        """Resets the iterator and returns itself for use in for-loops.

        Returns:
            Iterator[PerturbImage]: An iterator over `PybsmPerturber` instances.
        """
        self.n = 0
        return self

    @override
    def __next__(self) -> PerturbImage:
        """Returns the next `PybsmPerturber` instance with a unique parameter configuration.

        Returns:
            PerturbImage: A configured `PybsmPerturber` instance.

        Raises:
            StopIteration: When all configurations have been iterated over.
        """
        if self.n < len(self.sets):
            kwargs = {k: self.thetas[i][self.sets[self.n][i]] for i, k in enumerate(self.theta_keys)}
            func = PybsmPerturber(self.sensor, self.scenario, **kwargs)
            self.n: int = self.n + 1
            return func
        raise StopIteration

    @override
    def __getitem__(self, idx: int) -> PerturbImage:
        """Retrieves a specific `PybsmPerturber` instance by index.

        Args:
            idx (int): Index of the desired perturbation configuration.

        Returns:
            PerturbImage: The configured `PybsmPerturber` instance.

        Raises:
            IndexError: If the index is out of range.
        """
        if idx >= len(self.sets):
            raise IndexError("Index out of range")
        kwargs = {k: self.thetas[i][self.sets[idx][i]] for i, k in enumerate(self.theta_keys)}

        return PybsmPerturber(self.sensor, self.scenario, **kwargs)

    @property
    @override
    def thetas(self) -> Sequence[Sequence[Any]]:
        """Retrieves the current values for each parameter to be varied.

        Returns:
            Sequence[Sequence[Any]]: A sequence of parameter values for perturbation.
        """
        return self._thetas

    @property
    @override
    def theta_key(self) -> str:
        """Returns the parameter key associated with the perturbation settings.

        Returns:
            str: The parameter key name, "params".
        """
        return "params"

    @override
    @classmethod
    def get_default_config(cls) -> dict[str, Any]:
        """Retrieves the default configuration for `_PybsmPerturbImageFactory`.

        Returns:
            dict[str, Any]: A dictionary with the default configuration values.
        """
        cfg = super().get_default_config()

        # Remove perturber key if it exists
        cfg.pop("perturber", None)

        cfg["sensor"] = make_default_config([PybsmSensor])
        cfg["scenario"] = make_default_config([PybsmScenario])

        return cfg

    @override
    @classmethod
    def from_config(
        cls,
        config_dict: dict[str, Any],
        merge_default: bool = True,
    ) -> _PybsmPerturbImageFactory:
        """Instantiates a `_PybsmPerturbImageFactory` from a configuration dictionary.

        Args:
            config_dict (dict): Configuration dictionary with initialization parameters.
            merge_default (bool, optional): Whether to merge with default configuration. Defaults to True.

        Returns:
            C: An instance of `_PybsmPerturbImageFactory`.
        """
        config_dict = dict(config_dict)

        config_dict["sensor"] = from_config_dict(config_dict["sensor"], [PybsmSensor])
        config_dict["scenario"] = from_config_dict(config_dict["scenario"], [PybsmScenario])

        return super().from_config(config_dict, merge_default=merge_default)

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the `_PybsmPerturbImageFactory` instance.

        Returns:
            dict[str, Any]: Configuration dictionary with current settings.
        """
        return {
            "theta_keys": self.theta_keys,
            "sensor": to_config_dict(self.sensor),
            "scenario": to_config_dict(self.scenario),
            "thetas": self.thetas,
        }

    @classmethod
    def is_usable(cls) -> bool:
        """Checks if the required pybsm module is available.

        Returns:
            bool: True if pybsm is installed; False otherwise.
        """
        # Requires opencv to be installed
        return all([PybsmPerturber.is_usable(), PybsmScenario.is_usable(), PybsmSensor.is_usable()])


class CustomPybsmPerturbImageFactory(_PybsmPerturbImageFactory):
    """A customized version of `_PybsmPerturbImageFactory` with preset configurations.

    This factory extends `_PybsmPerturbImageFactory` to provide a specialized setup for
    creating `PybsmPerturber` instances with predefined sensor, scenario, and parameter values.
    """

    def __init__(
        self,
        sensor: PybsmSensor,
        scenario: PybsmScenario,
        theta_keys: Sequence[str],
        thetas: Sequence[Any],
    ) -> None:
        """Initializes the `CustomPybsmPerturbImageFactory` with sensor, scenario, and parameters.

        See https://pybsm.readthedocs.io/en/latest/explanation.html for image formation concepts and parameter details.

        Args:
            sensor (PybsmSensor): A pyBSM sensor object.
            scenario (PybsmScenario): A pyBSM scenario object.
            theta_keys (Sequence[str]): Names of perturbation parameters to vary.
            thetas (Sequence[Any]): Values to use for each perturbation parameter.
        """
        super().__init__(sensor, scenario, theta_keys, thetas)
