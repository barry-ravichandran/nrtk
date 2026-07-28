"""Defines RandomPerturbVideo, an interface for video perturbers that use random state.

Classes:
    RandomPerturbVideo: An abstract base class for video perturbation algorithms that require
        random number generation, providing standardized seed handling.

Dependencies:
    - nrtk.interfaces.PerturbVideo for the base interface.

Usage:
    To create a custom random video perturbation class, inherit from `RandomPerturbVideo`
    and implement the `_set_seed` and `perturb` methods.

Example:
    class CustomRandomPerturbVideo(RandomPerturbVideo):
        def _set_seed(self) -> None:
            if self._seed is not None:
                self._rng = np.random.default_rng(self._seed)

        def perturb(self, *, frames, **kwargs):
            # Custom perturbation logic using self._rng
            yield from frames

    perturber = CustomRandomPerturbVideo(seed=42)
    for frame in perturber(frames=iter(video_data)):
        # Consume perturbed frames here
        pass
"""

from __future__ import annotations

__all__: list[str] = ["RandomPerturbVideo"]

import abc
from typing import Any

from typing_extensions import override

from nrtk.interfaces import PerturbVideo


class RandomPerturbVideo(PerturbVideo):
    """Interface for video perturbers that use random state.

    Provides standardized seed handling for video perturbation algorithms.
    Subclasses must implement ``_set_seed()`` to initialize their random
    number generator(s).

    Attributes:
        seed: Random seed for reproducibility. None (default) means
            non-deterministic behavior.
    """

    def __init__(self, *, seed: int | None = None) -> None:
        """Initialize the RandomPerturbVideo with optional seed.

        Args:
            seed:
                Random seed for reproducible results. Defaults to None
                for non-deterministic behavior.
        """
        super().__init__()
        self._seed = seed
        self._set_seed()

    @property
    def seed(self) -> int | None:
        """Random seed for reproducibility. None means non-deterministic."""
        return self._seed

    @abc.abstractmethod
    def _set_seed(self) -> None:
        """Seed the random state(s) for this perturber.

        Implementations should initialize their random number generator(s)
        using ``self._seed``. If ``self._seed`` is ``None``, the RNG should
        be initialized without a seed for non-deterministic behavior.

        This method is called during ``__init__`` and may be called by
        concrete subclasses at the start of ``perturb()`` to ensure
        reproducible results across repeated calls.
        """

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the RandomPerturbVideo instance.

        Returns:
            Configuration dictionary containing seed setting.
        """
        cfg = super().get_config()
        cfg["seed"] = self._seed
        return cfg
