import json
import unittest.mock as mock
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pytest
from smqtk_core.configuration import (
    configuration_test_helper,
    from_config_dict,
    to_config_dict,
)

from nrtk.impls.perturb_image.generic.compose_perturber import ComposePerturber
from nrtk.impls.perturb_image.generic.nop_perturber import NOPPerturber
from nrtk.interfaces.perturb_image import PerturbImage

from ..test_perturber_utils import perturber_assertions


def _perturb(image: np.ndarray, additional_params: Optional[Dict[str, Any]] = None) -> np.ndarray:  # pragma: no cover
    return np.copy(image) + 1


m_dummy = mock.Mock(spec=PerturbImage)
m_dummy = _perturb


class TestComposePerturber:
    def test_consistency(self) -> None:
        """Run on a dummy image to ensure output matches precomputed results."""
        image = np.ones((3, 3, 3))

        # Test perturb interface directly
        inst = ComposePerturber(perturbers=[m_dummy, m_dummy])
        perturber_assertions(perturb=inst.perturb, image=image, expected=np.ones((3, 3, 3)) * 3)

        # Test callable
        perturber_assertions(
            perturb=ComposePerturber(perturbers=[m_dummy, m_dummy]),
            image=image,
            expected=np.ones((3, 3, 3)) * 3,
        )

    @pytest.mark.parametrize(
        ("image", "perturbers"),
        [
            (np.ones((256, 256, 3), dtype=np.float32), [m_dummy]),
            (np.ones((256, 256, 3), dtype=np.float64), [m_dummy, m_dummy]),
        ],
    )
    def test_reproducibility(self, image: np.ndarray, perturbers: List[PerturbImage]) -> None:
        """Ensure results are reproducible."""
        # Test perturb interface directly
        inst = ComposePerturber(perturbers=perturbers)
        out_image = perturber_assertions(perturb=inst.perturb, image=image, expected=None)
        perturber_assertions(perturb=inst.perturb, image=image, expected=out_image)

        # Test callable
        perturber_assertions(perturb=inst, image=image, expected=out_image)

    @pytest.mark.parametrize("perturbers", [[NOPPerturber()], [NOPPerturber(), NOPPerturber()]])
    def test_configuration(self, perturbers: List[PerturbImage]) -> None:
        """Test configuration stability."""
        inst = ComposePerturber(perturbers=perturbers)
        for i in configuration_test_helper(inst):
            for idx, perturber in enumerate(i.perturbers):
                assert perturber.get_config() == perturbers[idx].get_config()

    @pytest.mark.parametrize(
        "perturbers",
        [[NOPPerturber()], [NOPPerturber(), NOPPerturber()]],
    )
    def test_hydration(
        self,
        tmp_path: Path,
        perturbers: List[PerturbImage],
    ) -> None:
        """Test configuration hydration using from_config_dict."""
        original_perturber = ComposePerturber(perturbers=perturbers)

        original_perturber_config = original_perturber.get_config()

        config_file_path = tmp_path / "config.json"
        with open(str(config_file_path), "w") as f:
            json.dump(to_config_dict(original_perturber), f)

        with open(str(config_file_path)) as config_file:
            config = json.load(config_file)
            hydrated_perturber = from_config_dict(config, PerturbImage.get_impls())
            hydrated_perturber_config = hydrated_perturber.get_config()

            assert original_perturber_config == hydrated_perturber_config