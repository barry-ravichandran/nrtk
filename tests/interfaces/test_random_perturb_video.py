"""Tests for RandomPerturbVideo interface."""

from __future__ import annotations

from collections.abc import Generator, Iterator
from typing import Any

import numpy as np
import pytest
from smqtk_core.configuration import configuration_test_helper
from typing_extensions import override

from nrtk.interfaces import VideoFrame
from nrtk.interfaces._perturb_video import _perturb_guard
from nrtk.interfaces._random_perturb_video import RandomPerturbVideo


class _ConcreteRandomPerturbVideo(RandomPerturbVideo):
    """Minimal concrete subclass for testing RandomPerturbVideo."""

    _rng: np.random.Generator

    @override
    def _set_seed(self) -> None:
        self._rng = np.random.default_rng(self._seed)

    @override
    @_perturb_guard
    def perturb(
        self,
        *,
        frames: Iterator[VideoFrame],
        **additional_params: Any,
    ) -> Generator[VideoFrame, None, None]:
        yield from frames


@pytest.mark.core
class TestRandomPerturbVideo:
    def make_perturber(self, seed: int | None = None) -> RandomPerturbVideo:
        return _ConcreteRandomPerturbVideo(seed=seed)

    def test_seed_stored(self) -> None:
        inst = self.make_perturber(seed=42)
        assert inst.seed == 42

    def test_seed_none(self) -> None:
        inst = self.make_perturber(seed=None)
        assert inst.seed is None

    def test_get_config_includes_seed(self) -> None:
        inst = self.make_perturber(seed=42)
        cfg = inst.get_config()
        assert "seed" in cfg
        assert cfg["seed"] == 42

    def test_get_config_none_seed(self) -> None:
        inst = self.make_perturber(seed=None)
        cfg = inst.get_config()
        assert cfg["seed"] is None

    @pytest.mark.parametrize("seed", [42, None, 0, 123456])
    def test_configuration_round_trip(self, seed: int | None) -> None:
        inst = self.make_perturber(seed=seed)
        for i in configuration_test_helper(inst):
            assert i.seed == seed
