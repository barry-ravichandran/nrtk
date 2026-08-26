"""Fakes and test doubles shared across the test suite."""

from __future__ import annotations

from collections.abc import Generator, Hashable, Iterable, Iterator, Sequence
from copy import deepcopy
from typing import Any

import numpy as np
from smqtk_image_io.bbox import AxisAlignedBoundingBox
from typing_extensions import override

from nrtk.interfaces import PerturbFactory, PerturbImage, PerturbImageFactory, PerturbVideo, VideoFrame
from nrtk.interfaces._perturb_data import PerturbData


class FakeDeviceTensor:
    """Array-like that refuses numpy conversion until it is moved to the host.

    Stands in for a device tensor without needing torch or a GPU: a path reaching
    for ``np.asarray`` instead of ``to_numpy`` fails here, where a CPU tensor
    would convert fine and hide the bug.
    """

    def __init__(self, array: np.ndarray) -> None:
        self._array = np.asarray(array)

    def detach(self) -> FakeDeviceTensor:
        return self

    def cpu(self) -> np.ndarray:
        return self._array.copy()  # a real .cpu() allocates a fresh host buffer

    def __array__(self, dtype: Any = None, copy: bool | None = None) -> np.ndarray:  # noqa: ANN401
        raise TypeError("can't convert cuda:0 device type tensor to numpy")


class FakeImagePerturber(PerturbImage):
    """Fake image perturber for testing purposes.

    Accepts arbitrary keyword arguments and returns them via get_config().
    This allows it to be used with any theta_key in factory tests.

    Default parameters param1 and param2 are provided for common test cases.

    With in_place_fill set, perturb() writes that value into the image it is given
    and returns that same buffer rather than a copy, which is what lets a test tell
    whether an adapter really copied before handing the image over.
    """

    def __init__(
        self,
        *,
        param1: float = 1,
        param2: float = 2,
        in_place_fill: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.param1 = param1
        self.param2 = param2
        self.in_place_fill = in_place_fill
        self._extra_kwargs = kwargs

    @override
    def perturb(
        self,
        *,
        image: np.ndarray[Any, Any],
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None = None,
        **_: Any,
    ) -> tuple[
        np.ndarray[Any, Any],
        Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None,
    ]:  # pragma: no cover
        if self.in_place_fill is not None:
            image[...] = self.in_place_fill
            return image, boxes
        return np.copy(image), deepcopy(boxes)

    @override
    def get_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {"param1": self.param1, "param2": self.param2}
        # Only when set, so the factory tests' expected_config dicts stay as they are.
        if self.in_place_fill is not None:
            config["in_place_fill"] = self.in_place_fill
        config.update(self._extra_kwargs)
        return config


class FakeVideoPerturber(PerturbVideo):
    """Fake video perturber for testing purposes.

    Accepts arbitrary keyword arguments and returns them via get_config().
    This allows it to be used with any theta_key in factory tests.

    Default parameters param1 and param2 are provided for common test cases.
    """

    def __init__(self, *, param1: float = 1, param2: float = 2, **kwargs: Any) -> None:
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        self._extra_kwargs = kwargs

    @override
    def perturb(
        self,
        *,
        frames: Iterator[VideoFrame],
        **additional_params: Any,
    ) -> Generator[VideoFrame, None, None]:  # pragma: no cover
        for frame in frames:
            yield deepcopy(frame)

    @override
    def get_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {"param1": self.param1, "param2": self.param2}
        config.update(self._extra_kwargs)
        return config


class FakePerturbFactory(PerturbFactory):
    """Fake factory for testing purposes.

    A minimal concrete implementation of PerturbFactory that can be used
    to test interface behavior without depending on any specific implementation.
    """

    def __init__(
        self,
        *,
        perturber: type[PerturbData],
        theta_key: str,
        theta_values: Sequence[Any],
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(perturber=perturber, theta_key=theta_key, perturber_kwargs=perturber_kwargs)
        self._theta_values = list(theta_values)

    @property
    @override
    def thetas(self) -> Sequence[Any]:
        return self._theta_values

    @override
    def __getitem__(self, idx: int) -> PerturbData:
        return self._create_perturber({self._theta_key: self._theta_values[idx]})

    @override
    def get_config(self) -> dict[str, Any]:
        return {
            "perturber": self._perturber.get_type_string(),
            "theta_key": self._theta_key,
            "theta_values": self._theta_values,
            "perturber_kwargs": self._perturber_kwargs,
        }


class FakePerturbImageFactory(PerturbImageFactory):
    """Deprecated, kept for backward compat while PerturbImageFactory still exists.

    A minimal concrete implementation of PerturbImageFactory that can be used
    to test interface behavior without depending on any specific implementation.
    """

    def __init__(
        self,
        *,
        perturber: type[PerturbImage],
        theta_key: str,
        theta_values: Sequence[Any],
        perturber_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(perturber=perturber, theta_key=theta_key, perturber_kwargs=perturber_kwargs)
        self._theta_values = list(theta_values)

    @property
    @override
    def thetas(self) -> Sequence[Any]:
        return self._theta_values

    @override
    def __getitem__(self, idx: int) -> PerturbImage:
        return self._create_perturber({self._theta_key: self._theta_values[idx]})

    @override
    def get_config(self) -> dict[str, Any]:
        return {
            "perturber": self._perturber.get_type_string(),
            "theta_key": self._theta_key,
            "theta_values": self._theta_values,
            "perturber_kwargs": self._perturber_kwargs,
        }
