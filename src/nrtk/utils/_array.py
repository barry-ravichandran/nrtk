"""Helpers for converting array-likes into numpy arrays.

Functions:
    to_numpy: Convert an array-like to a numpy array, via host memory if needed.
"""

__all__ = ["to_numpy"]

from typing import Any

import numpy as np


def to_numpy(value: Any, *, copy: bool = False) -> np.ndarray[Any, Any]:  # noqa: ANN401
    """Convert an array-like to a numpy array, via host memory if needed.

    Duck-typed rather than keyed off ``isinstance(value, torch.Tensor)`` so it
    stays usable in modules that must import without ``torch`` installed.

    Returns a view sharing storage with a numpy array or host tensor; a device
    tensor arrives as a fresh buffer because moving it off the device copied it.

    Args:
        value: Array-like to convert. A sequence *containing* tensors is not
            handled, since only the sequence itself is inspected.
        copy: Guarantee the result shares no storage with ``value``. This is not
            :func:`numpy.asarray`'s numpy 2 ``copy``, whose ``False`` forbids
            copying; here it only means a copy is not required.

    Returns:
        The value as a numpy array backed by host memory.
    """
    if hasattr(value, "detach"):  # torch tensor, possibly on an accelerator
        tensor = value.detach()
        value = tensor.cpu()
        # .cpu() returns the tensor itself when it is already on the host, so a
        # new object means the device transfer allocated a fresh buffer for us.
        if value is not tensor:
            copy = False

    array = np.asarray(value)

    return array.copy() if copy else array
