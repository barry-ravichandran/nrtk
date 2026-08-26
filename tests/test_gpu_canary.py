"""Fail an environment that requests a GPU but cannot use CUDA.

The device tests skip themselves when no GPU is visible, so without this a GPU
job with a broken CUDA stack goes green having exercised nothing. Same idea as
``tests/test_guard_canaries.py``.
"""

from __future__ import annotations

import os

import pytest

# "" is how the CPU-only tox environments blank the variable; "-1" is the
# conventional way to ask CUDA for no devices at all.
_NO_DEVICE_REQUESTED = {"", "-1"}


def _requested_devices() -> str | None:
    """Return the requested device list, or None if the environment asks for no GPU."""
    value = os.environ.get("CUDA_VISIBLE_DEVICES")
    if value is None or value.strip() in _NO_DEVICE_REQUESTED:
        return None
    return value


# No require_marker fixture, unlike the guard canaries: the gate here is the
# environment variable, so an environment that requests no device self-skips below.
@pytest.mark.diffusion
def test_cuda_usable_when_devices_are_requested() -> None:
    """Fail when ``CUDA_VISIBLE_DEVICES`` requests a GPU that torch cannot use."""
    devices = _requested_devices()
    if devices is None:
        pytest.skip("CUDA_VISIBLE_DEVICES requests no device; this environment is CPU-only by design")

    try:
        import torch
    except ImportError:
        pytest.fail(
            f"CUDA_VISIBLE_DEVICES={devices!r} requests a GPU, but torch is not installed. "
            "This environment cannot exercise a single device-transfer path.",
        )

    if not torch.cuda.is_available():
        pytest.fail(
            f"CUDA_VISIBLE_DEVICES={devices!r} requests a GPU, but torch.cuda.is_available() is False "
            f"(torch {torch.__version__}). The GPU-gated tests would skip and this job would pass "
            "without exercising a single device-transfer path. Usually the runner's NVIDIA driver is "
            "older than this torch build's bundled CUDA runtime -- see the GPU driver and CUDA "
            "compatibility section of docs/development/system_requirements.rst.",
        )
