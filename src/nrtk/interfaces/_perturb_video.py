"""Defines PerturbVideo, an interface for implementing algorithms that generate perturbed videos.

Classes:
    PerturbVideo: An abstract base class that specifies the structure for video perturbation
    algorithms, allowing for different perturbation techniques to be implemented.

Dependencies:
    - numpy for handling image arrays.
    - smqtk_core for configurable plugin interface capabilities.

Usage:
    To create a custom video perturbation class, inherit from `PerturbVideo` and implement
    the `perturb` method, defining the specific perturbation logic.

Example:
    class CustomPerturbVideo(PerturbVideo):
        def perturb(self, frames, additional_params=None):
            # Custom perturbation logic here
            pass

    perturber = CustomPerturbVideo()
    for frame in perturber(video_data):
        # Consume perturbed frames here
        pass
"""

from __future__ import annotations

import abc
from collections.abc import Callable, Generator, Hashable, Iterable, Iterator
from functools import wraps
from typing import Any, Concatenate, TypeVar, cast

import numpy as np
from smqtk_image_io.bbox import AxisAlignedBoundingBox
from typing_extensions import ParamSpec

from nrtk.interfaces._plugfigurable import Plugfigurable


class VideoFrame:
    """Data structure representing one frame of video, for use with the PerturbVideo interface.

    Attributes:
        image (ndarray)
            The frame image as a numpy array.
        timestamp (float)
            The frame timestamp in seconds since the beginning of the video.
        boxes (Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None)
            Bounding boxes of detections in the image.
        additional_params (dict[str, Any] | None)
            Implementation-defined parameter-value pairs specific to this frame.
    """

    def __init__(
        self,
        *,
        image: np.ndarray[Any, Any],
        timestamp: float,
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None = None,
        additional_params: dict[str, Any] | None = None,
    ) -> None:
        self.image = image
        self.timestamp = timestamp
        self.boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] = boxes if boxes is not None else []
        self.additional_params: dict[str, Any] = additional_params if additional_params is not None else {}


class PerturbVideo(Plugfigurable):
    """Algorithm that generates a perturbed video for given input video stimulus."""

    def __init__(self) -> None:
        """Initializes the PerturbVideo."""
        self.active: bool = False

    @abc.abstractmethod
    def perturb(
        self,
        *,
        frames: Iterator[VideoFrame],
        **additional_params: Any,
    ) -> Generator[VideoFrame, None, None]:
        """Generate a perturbed video for the given video stimulus.

        Note perturbers that resize, rotate, or similarly affect the dimensions of an image may impact
        scoring if bounding boxes are not similarly transformed. No mutable objects passed in, such as the
        frame image, should be modified in place; only copies should be modified and returned.

        :param frames: Iterator of VideoFrame objects containing input frame data.

        :param additional_params: A dictionary containing implementation-defined input parameter-value pairs
            applicable to the entire video.

        Returns:
            A generator yielding VideoFrame objects, each containing perturbed data for one frame.
        """
        ...

    def __call__(
        self,
        *,
        frames: Iterator[VideoFrame],
        **additional_params: Any,
    ) -> Generator[VideoFrame, None, None]:
        """Calls ``perturb()`` with the given input video."""
        return self.perturb(frames=frames, **additional_params)

    @classmethod
    def get_type_string(cls) -> str:
        """Returns the fully qualified type string of the `PerturbVideo` class or its subclass.

        Returns:
            A string representing the fully qualified type, in the format `<module>.<class_name>`.
            For example, "my_module.CustomPerturbVideo".
        """
        return f"{cls.__module__}.{cls.__name__}"

    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the PerturbVideo instance.

        Returns:
            dict[str, Any]: Configuration dictionary with current settings.
        """
        return {}


S = TypeVar("S", bound=PerturbVideo)
P = ParamSpec("P")


def _perturb_guard(
    fn: Callable[Concatenate[S, P], Generator[VideoFrame, None, None]],
) -> Callable[Concatenate[S, P], Generator[VideoFrame, None, None]]:
    """Wraps PerturbVideo.perturb() implementations to provide input validation.

    Args:
        fn:
            PerturbVideo.perturb() function to wrap.

    Raises:
        RuntimeError: If perturb() is called again before the previous perturb() is complete.
        ValueError: If frame shape, data type, or timestamp is not consistent across the video.
    """

    @wraps(fn)
    def _wrapper(self: S, /, *args: P.args, **kwargs: P.kwargs) -> Generator[VideoFrame, None, None]:
        if self.active:
            raise RuntimeError("Cannot call perturb() while previous perturb() is incomplete.")

        kwargs["frames"] = _FrameConsistencyIterator(cast(Iterator[VideoFrame], kwargs["frames"]))

        try:
            self.active = True
            yield from fn(self, *args, **kwargs)  # noqa: FKA100, RUF100
        finally:
            self.active = False

    return _wrapper


class _FrameConsistencyIterator:
    """Used by _perturb_guard to perform sanity checks across the length of a video."""

    def __init__(self, frames: Iterator[VideoFrame]) -> None:
        self.frames = frames

        self.prev_timestamp: float | None
        self.frame_shape: tuple[int, ...] | None
        self.frame_dtype: np.dtype | None

    def __iter__(self) -> Iterator[VideoFrame]:
        self.prev_timestamp = None
        self.frame_shape = None
        self.frame_dtype = None
        return self

    def __next__(self) -> VideoFrame:
        frame = next(self.frames)
        self._check_frame(frame)
        return frame

    def _check_frame(self, frame: VideoFrame) -> None:
        self._check_timestamp(frame)
        self._check_frame_shape(frame)
        self._check_frame_dtype(frame)

    def _check_timestamp(self, frame: VideoFrame) -> None:
        if self.prev_timestamp is not None and self.prev_timestamp >= frame.timestamp:
            raise ValueError(
                f"Sequential frame timestamps are not increasing: {self.prev_timestamp} -> {frame.timestamp}.",
            )
        self.prev_timestamp = frame.timestamp

    def _check_frame_shape(self, frame: VideoFrame) -> None:
        if self.frame_shape is None:
            if len(frame.image.shape) not in [2, 3]:
                raise ValueError(f"Frame image must have 2 or 3 dimensions; instead given {len(frame.image.shape)}.")
            if frame.image.size == 0:
                raise ValueError("Empty frame image.")
            self.frame_shape = frame.image.shape
        elif self.frame_shape != frame.image.shape:
            raise ValueError(
                f"Sequential frame images do not have the same shape: {self.frame_shape} -> {frame.image.shape}.",
            )

    def _check_frame_dtype(self, frame: VideoFrame) -> None:
        if self.frame_dtype is None:
            self.frame_dtype = frame.image.dtype
        elif self.frame_dtype != frame.image.dtype:
            raise ValueError(
                f"Sequential frame images do not have the same data type: {self.frame_dtype} -> {frame.image.dtype}.",
            )
