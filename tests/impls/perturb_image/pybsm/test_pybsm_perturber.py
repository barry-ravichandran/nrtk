import unittest.mock as mock
from collections.abc import Hashable, Iterable
from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image
from smqtk_core.configuration import configuration_test_helper
from smqtk_image_io.bbox import AxisAlignedBoundingBox
from syrupy.assertion import SnapshotAssertion

from nrtk.impls.perturb_image.pybsm.pybsm_perturber import PybsmPerturber
from nrtk.utils._exceptions import PyBSMImportError
from tests.impls.perturb_image.test_perturber_utils import pybsm_perturber_assertions
from tests.impls.test_pybsm_utils import create_sample_sensor_and_scenario

INPUT_IMG_FILE = "./docs/examples/pybsm/data/M-41 Walker Bulldog (USA) width 319cm height 272cm.tiff"
EXPECTED_IMG_FILE = "./tests/impls/perturb_image/pybsm/data/Expected Output.tiff"

np.random.seed(42)  # noqa: NPY002


@pytest.mark.skipif(not PybsmPerturber.is_usable(), reason=str(PyBSMImportError()))
class TestPyBSMPerturber:
    def test_consistency(self) -> None:
        """Run on a dummy image to ensure output matches precomputed results."""
        image = np.array(Image.open(INPUT_IMG_FILE))
        expected = np.array(Image.open(EXPECTED_IMG_FILE))
        img_gsd = 3.19 / 160.0
        sensor, scenario = create_sample_sensor_and_scenario()
        # Test perturb interface directly
        inst = PybsmPerturber(sensor=sensor, scenario=scenario, ground_range=10000)
        pybsm_perturber_assertions(
            perturb=inst.perturb,
            image=image,
            expected=expected,
            additional_params={"img_gsd": img_gsd},
        )

        # Test callable
        pybsm_perturber_assertions(
            perturb=PybsmPerturber(sensor=sensor, scenario=scenario, ground_range=10000),
            image=image,
            expected=expected,
            additional_params={"img_gsd": img_gsd},
        )

    @pytest.mark.parametrize(
        ("param_name", "param_value", "rng_seed"),
        [
            ("ground_range", 10000, 1),
            ("ground_range", 20000, 1),
            ("ground_range", 30000, 2),
            ("altitude", 10000, 2),
            ("ihaze", 2, 2),
        ],
    )
    def test_reproducibility(self, param_name: str, param_value: int, rng_seed: int) -> None:
        """Ensure results are reproducible."""
        # Test perturb interface directly
        image = np.array(Image.open(INPUT_IMG_FILE))
        sensor, scenario = create_sample_sensor_and_scenario()
        # For type: ignore below, see https://github.com/microsoft/pyright/issues/5545#issuecomment-1644027877
        inst = PybsmPerturber(sensor=sensor, scenario=scenario, rng_seed=rng_seed, **{param_name: param_value})  # type: ignore
        img_gsd = 3.19 / 160.0
        out_image = pybsm_perturber_assertions(
            perturb=inst.perturb,
            image=image,
            expected=None,
            additional_params={"img_gsd": img_gsd},
        )
        pybsm_perturber_assertions(
            perturb=inst.perturb,
            image=image,
            expected=out_image,
            additional_params={"img_gsd": img_gsd},
        )

    def test_configuration(self) -> None:
        """Test configuration stability."""
        sensor, scenario = create_sample_sensor_and_scenario()
        inst = PybsmPerturber(sensor=sensor, scenario=scenario)
        for i in configuration_test_helper(inst):
            assert i.sensor.name == sensor.name
            assert i.sensor.D == sensor.D
            assert i.sensor.f == sensor.f
            assert i.sensor.p_x == sensor.p_x
            assert np.array_equal(i.sensor.opt_trans_wavelengths, sensor.opt_trans_wavelengths)
            assert np.array_equal(i.sensor.optics_transmission, sensor.optics_transmission)
            assert i.sensor.eta == sensor.eta
            assert i.sensor.w_x == sensor.w_x
            assert i.sensor.w_y == sensor.w_y
            assert i.sensor.int_time == sensor.int_time
            assert i.sensor.n_tdi == sensor.n_tdi
            assert i.sensor.dark_current == sensor.dark_current
            assert i.sensor.read_noise == sensor.read_noise
            assert i.sensor.max_n == sensor.max_n
            assert i.sensor.bit_depth == sensor.bit_depth
            assert i.sensor.max_well_fill == sensor.max_well_fill
            assert i.sensor.s_x == sensor.s_x
            assert i.sensor.s_y == sensor.s_y
            assert i.sensor.da_x == sensor.da_x
            assert i.sensor.da_y == sensor.da_y
            assert np.array_equal(i.sensor.qe_wavelengths, sensor.qe_wavelengths)
            assert np.array_equal(i.sensor.qe, sensor.qe)

            assert i.scenario.name == scenario.name
            assert i.scenario.ihaze == scenario.ihaze
            assert i.scenario.altitude == scenario.altitude
            assert i.scenario.ground_range == scenario.ground_range
            assert i.scenario.aircraft_speed == scenario.aircraft_speed
            assert i.scenario.target_reflectance == scenario.target_reflectance
            assert i.scenario.target_temperature == scenario.target_temperature
            assert i.scenario.background_reflectance == scenario.background_reflectance
            assert i.scenario.background_temperature == scenario.background_temperature
            assert i.scenario.ha_wind_speed == scenario.ha_wind_speed
            assert i.scenario.cn2_at_1m == scenario.cn2_at_1m

            assert np.array_equal(i.reflectance_range, inst.reflectance_range)

    @pytest.mark.parametrize(
        ("reflectance_range", "expectation"),
        [
            (np.array([0.05, 0.5]), does_not_raise()),
            (np.array([0.01, 0.5]), does_not_raise()),
            (
                np.array([0.05]),
                pytest.raises(ValueError, match=r"Reflectance range array must have length of 2"),
            ),
            (
                np.array([0.5, 0.05]),
                pytest.raises(
                    ValueError,
                    match=r"Reflectance range array values must be strictly ascending",
                ),
            ),
        ],
    )
    def test_configuration_bounds(self, reflectance_range: np.ndarray, expectation: AbstractContextManager) -> None:
        """Test that an exception is properly raised (or not) based on argument value."""
        sensor, scenario = create_sample_sensor_and_scenario()
        with expectation:
            PybsmPerturber(sensor=sensor, scenario=scenario, reflectance_range=reflectance_range)

    @pytest.mark.parametrize(
        ("additional_params", "expectation"),
        [
            ({"img_gsd": 3.19 / 160.0}, does_not_raise()),
            (
                {},
                pytest.raises(
                    ValueError,
                    match=r"'img_gsd' must be present in image metadata for this perturber",
                ),
            ),
        ],
    )
    def test_additional_params(self, additional_params: dict[str, Any], expectation: AbstractContextManager) -> None:
        """Test variations of additional params."""
        sensor, scenario = create_sample_sensor_and_scenario()
        perturber = PybsmPerturber(sensor=sensor, scenario=scenario, reflectance_range=np.array([0.05, 0.5]))
        image = np.array(Image.open(INPUT_IMG_FILE))
        with expectation:
            _ = perturber(image, additional_params=additional_params)

    @pytest.mark.parametrize(
        "boxes",
        [
            None,
            [(AxisAlignedBoundingBox((0, 0), (123, 236)), {"test": 0.0})],
            [
                (AxisAlignedBoundingBox((132, 222), (444, 352)), {"test": 0.7}),
                (AxisAlignedBoundingBox((231, 111), (333, 212)), {"test2": 1.0}),
            ],
        ],
    )
    def test_perturb_with_boxes(
        self,
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]],
        snapshot: SnapshotAssertion,
    ) -> None:
        """Test that bounding boxes scale as expected during perturb."""
        image = np.array(Image.open(INPUT_IMG_FILE))
        sensor, scenario = create_sample_sensor_and_scenario()
        inst = PybsmPerturber(sensor=sensor, scenario=scenario)
        _, out_boxes = inst.perturb(image, boxes=boxes, additional_params={"img_gsd": 3.19 / 160})
        assert out_boxes == snapshot

    @mock.patch.object(PybsmPerturber, "is_usable")
    def test_missing_deps(self, mock_is_usable: MagicMock) -> None:
        """Test that an exception is raised when required dependencies are not installed."""
        mock_is_usable.return_value = False
        assert not PybsmPerturber.is_usable()
        sensor, scenario = create_sample_sensor_and_scenario()
        with pytest.raises(PyBSMImportError):
            PybsmPerturber(sensor=sensor, scenario=scenario)
