from collections.abc import Hashable
from typing import Any, cast
from unittest.mock import MagicMock

import numpy as np
import pytest
from pybsm.simulation import ImageSimulator
from smqtk_image_io.bbox import AxisAlignedBoundingBox
from typing_extensions import override

from nrtk.impls.perturb_image.optical._pybsm.pybsm_perturber_mixin import PybsmPerturberMixin


class DummyPybsmPerturber(PybsmPerturberMixin):
    """Dummy perturber implementation to test abstract mixin class."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._simulator = self._create_simulator()

    @override
    def _create_simulator(self) -> ImageSimulator:
        return MagicMock(spec=ImageSimulator)


@pytest.mark.pybsm
@pytest.mark.parametrize(
    ("wavelengths", "message"),
    [
        (np.array([]), "opt_trans_wavelengths must contain at least two values"),
        (np.array([100.0]), "opt_trans_wavelengths must contain at least two values"),
        (np.array([100.0, 100.0, 200.0]), "opt_trans_wavelengths must be strictly ascending"),
        (np.array([100.0, 300.0, 200.0]), "opt_trans_wavelengths must be strictly ascending"),
        (np.array([100.0, 100.0]), "opt_trans_wavelengths must be strictly ascending"),
        (np.array([200.0, 100.0]), "opt_trans_wavelengths must be strictly ascending"),
        (np.array([1.0, np.inf]), "opt_trans_wavelengths must contain only finite values"),
        (np.array([100.0, np.nan]), "opt_trans_wavelengths must contain only finite values"),
        (np.array([100.0, np.inf, 200.0]), "opt_trans_wavelengths must contain only finite values"),
        (np.array([100.0, np.nan, 200.0]), "opt_trans_wavelengths must contain only finite values"),
        (np.array(5), "opt_trans_wavelengths must be one-dimensional"),
        (np.array([[100.0, 200.0]]), "opt_trans_wavelengths must be one-dimensional"),
        (np.array([-100.0, 101.0]), "opt_trans_wavelengths must contain only positive values"),
        (np.array([0.0, 101.0]), "opt_trans_wavelengths must contain only positive values"),
        (np.array([100.0, 101.0]), None),
        (np.array([100.0, 200.0]), None),
        (np.array([100.0, 200.0, 300.0]), None),
    ],
)
def test_check_opt_trans_wavelengths(wavelengths: np.ndarray, message: str | None) -> None:
    """Test optical transmission wavelength validation."""
    perturber = DummyPybsmPerturber()
    if message is None:
        perturber._check_opt_trans_wavelengths(wavelengths)
    else:
        with pytest.raises(ValueError, match=message):
            perturber._check_opt_trans_wavelengths(wavelengths)


@pytest.mark.pybsm
@pytest.mark.parametrize(
    ("boxes", "expected_boxes"),
    [
        (
            [
                (AxisAlignedBoundingBox(min_vertex=(6, 4), max_vertex=(9, 8)), {"test": 1.0}),
            ],
            [(AxisAlignedBoundingBox(min_vertex=(4, 2), max_vertex=(6, 4)), {"test": 1.0})],
        ),
        ([], []),
        (None, None),
    ],
)
def test_handle_boxes_and_format(
    boxes: list[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None,
    expected_boxes: list[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None,
) -> None:
    """Test clipping and scaling."""
    perturber = DummyPybsmPerturber()
    image = np.full((64, 48, 3), 256.0)
    expected_image = np.full((64, 48, 3), 255, dtype=np.uint8)

    image_out, boxes_out = perturber._handle_boxes_and_format(sim_img=image, boxes=boxes, orig_shape=(128, 72, 3))

    assert np.array_equal(image_out, expected_image)
    assert image_out.dtype == expected_image.dtype
    assert boxes_out == expected_boxes


@pytest.mark.pybsm
@pytest.mark.parametrize("value", [1, 2])
def test_init_valid_ihaze(value: int) -> None:
    """Test ihaze validation."""
    DummyPybsmPerturber(ihaze=value)


@pytest.mark.pybsm
def test_init_invalid_ihaze() -> None:
    """Test ihaze validation."""
    with pytest.raises(ValueError, match="Invalid ihaze value"):
        DummyPybsmPerturber(ihaze=99)


@pytest.mark.pybsm
@pytest.mark.parametrize("value", [2, 500, 1000, 5000, 12000, 14000, 18000, 20000, 24500, 1000000])
def test_init_valid_altitude(value: float) -> None:
    """Test altitude validation."""
    DummyPybsmPerturber(altitude=value)


@pytest.mark.pybsm
def test_init_invalid_altitude() -> None:
    """Test altitude validation."""
    with pytest.raises(ValueError, match="Invalid altitude value"):
        DummyPybsmPerturber(altitude=99)


@pytest.mark.pybsm
@pytest.mark.parametrize("value", [0, 100, 500, 1000, 10000, 20000, 22000, 78000, 85000, 100000, 300000])
def test_init_valid_ground_range(value: float) -> None:
    """Test ground_range validation."""
    DummyPybsmPerturber(ground_range=value)


@pytest.mark.pybsm
def test_init_invalid_ground_range() -> None:
    """Test ground_range validation."""
    with pytest.raises(ValueError, match="Invalid ground range value"):
        DummyPybsmPerturber(ground_range=99)


@pytest.mark.pybsm
def test_optics_transmission_default() -> None:
    """Test optics_transmission default value."""
    perturber = DummyPybsmPerturber(opt_trans_wavelengths=np.array([100, 200, 400]), optics_transmission=None)
    assert np.array_equal(perturber.optics_transmission, np.array([1.0, 1.0, 1.0]))


@pytest.mark.pybsm
def test_pw_xy_default() -> None:
    """Test default values of p_y, w_x, w_y."""
    perturber = DummyPybsmPerturber(p_x=1.23, p_y=None, w_x=None, w_y=None)
    assert perturber.p_y == perturber.p_x
    assert perturber.w_x == perturber.p_x
    assert perturber.w_y == perturber.p_x


@pytest.mark.pybsm
def test_qe_wavelengths_default() -> None:
    """Test qe_wavelengths default value."""
    perturber = DummyPybsmPerturber(opt_trans_wavelengths=np.array([100, 200, 400]), qe_wavelengths=None)
    assert np.array_equal(perturber.qe_wavelengths, perturber.opt_trans_wavelengths)
    assert not np.shares_memory(perturber.qe_wavelengths, perturber.opt_trans_wavelengths)


@pytest.mark.pybsm
def test_qe_default() -> None:
    """Test qe default value."""
    perturber = DummyPybsmPerturber(opt_trans_wavelengths=np.array([100, 200, 400]), qe=None)
    assert np.array_equal(perturber.qe, np.array([1.0, 1.0, 1.0]))


@pytest.mark.pybsm
def test_img_gsd_none() -> None:
    """Test img_gsd validation."""
    perturber = DummyPybsmPerturber()
    with pytest.raises(ValueError, match="img_gsd must be provided"):
        perturber.perturb(image=np.ones((10, 10, 3), dtype=np.uint8))


@pytest.mark.pybsm
@pytest.mark.parametrize(("use_default_psf", "called_gsd"), [(False, 2.0), (True, None)])
def test_img_gsd_default_psf(use_default_psf: bool, called_gsd: float | None) -> None:
    """Test img_gsd validation."""
    perturber = DummyPybsmPerturber()
    perturber._use_default_psf = use_default_psf
    mock_simulate_image = cast(MagicMock, perturber._simulator.simulate_image)
    mock_simulate_image.return_value = (None, np.zeros((10, 10, 3), dtype=np.uint8), None)
    perturber.perturb(image=np.ones((10, 10, 3), dtype=np.uint8), img_gsd=2.0)

    mock_simulate_image.assert_called_once()
    assert mock_simulate_image.call_args.kwargs == {"gsd": called_gsd}


@pytest.mark.pybsm
@pytest.mark.parametrize(
    ("add_noise", "noisy_image", "use_noisy_image"),
    [
        (False, None, False),
        (False, np.full((10, 10, 3), 255, dtype=np.uint8), False),
        (True, None, False),
        (True, np.full((10, 10, 3), 255, dtype=np.uint8), True),
    ],
)
def test_use_noisy_image(add_noise: bool, noisy_image: np.ndarray | None, use_noisy_image: bool) -> None:
    """Test logic on when to return noisy vs blurry image."""
    perturber = DummyPybsmPerturber()
    mock_simulator = cast(MagicMock, perturber._simulator)
    mock_simulator.add_noise = add_noise
    blur_image = np.zeros((10, 10, 3), dtype=np.uint8)
    mock_simulate_image = cast(MagicMock, perturber._simulator.simulate_image)
    mock_simulate_image.return_value = (None, blur_image, noisy_image)
    out_image, _ = perturber.perturb(image=np.ones((10, 10, 3), dtype=np.uint8), img_gsd=2.0)
    if use_noisy_image:
        assert noisy_image is not None
        assert np.array_equal(out_image, noisy_image)
    else:
        assert np.array_equal(out_image, blur_image)
