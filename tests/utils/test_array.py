"""Unit tests for the array conversion helpers in :mod:`nrtk.utils._array`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from nrtk.utils._array import to_numpy

pytestmark = pytest.mark.core

EXPECTED = np.arange(12, dtype=np.float32).reshape((3, 4))


def _numpy_array() -> Any:  # noqa: ANN401
    return EXPECTED.copy()


def _plain_sequence() -> Any:  # noqa: ANN401
    return EXPECTED.tolist()


def _cpu_tensor() -> Any:  # noqa: ANN401
    torch = pytest.importorskip("torch")
    return torch.arange(12, dtype=torch.float32).reshape((3, 4))


def _grad_tensor() -> Any:  # noqa: ANN401
    """A tensor still attached to the autograd graph; ``np.asarray`` raises on these."""
    torch = pytest.importorskip("torch")
    return torch.arange(12, dtype=torch.float32).reshape((3, 4)).requires_grad_(True)


def _cuda_tensor() -> Any:  # noqa: ANN401
    """A device-resident tensor; ``np.asarray`` raises on these."""
    torch = pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.skip("CUDA is not available")
    return torch.arange(12, dtype=torch.float32, device="cuda").reshape((3, 4))


def _host_view(value: Any) -> np.ndarray:  # noqa: ANN401
    """The caller's own buffer, for aliasing comparisons."""
    return value.detach().cpu().numpy() if hasattr(value, "detach") else value


@pytest.mark.parametrize(
    "make_input",
    [
        _numpy_array,
        _plain_sequence,
        pytest.param(_cpu_tensor, marks=pytest.mark.diffusion),
        pytest.param(_grad_tensor, marks=pytest.mark.diffusion),
        pytest.param(_cuda_tensor, marks=pytest.mark.diffusion),
    ],
)
def test_converts_to_host_numpy(make_input: Callable[[], Any]) -> None:
    """Anything array-like converts to an equal host-backed numpy array."""
    result = to_numpy(make_input())

    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, EXPECTED)


@pytest.mark.parametrize(
    ("make_input", "aliases_by_default"),
    [
        (_numpy_array, True),
        pytest.param(_cpu_tensor, True, marks=pytest.mark.diffusion),
        pytest.param(_cuda_tensor, False, marks=pytest.mark.diffusion),
    ],
)
def test_copy_never_aliases_the_input(make_input: Callable[[], Any], aliases_by_default: bool) -> None:
    """``copy=True`` never shares storage; the default may, depending on where the input lived."""
    value = make_input()
    host = _host_view(value)

    assert not np.shares_memory(to_numpy(value, copy=True), host)
    assert bool(np.shares_memory(to_numpy(value), host)) is aliases_by_default
