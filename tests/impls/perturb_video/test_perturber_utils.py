from collections.abc import Callable, Generator, Iterator
from copy import deepcopy
from typing import Any

import numpy as np

from nrtk.interfaces import VideoFrame


class FrameRepeater:
    """Repeats a given video frame n times, for succinct testing data."""

    def __init__(self, frame: VideoFrame, n: int, fps: float = 30.0) -> None:
        self.frame = frame
        self.n = n
        self.i = 0
        self.fps = fps

    def __iter__(self) -> Iterator[VideoFrame]:
        return FrameRepeater(frame=self.frame, n=self.n, fps=self.fps)

    def __next__(self) -> VideoFrame:
        if self.i < self.n:
            frame = deepcopy(self.frame)
            frame.timestamp += self.i / self.fps
            self.i += 1
            return frame
        raise StopIteration


class FrameRecorder:
    """Records each video frame that comes from an Iterator, for testing purposes."""

    def __init__(self, frames: Iterator[VideoFrame]) -> None:
        self.frames = iter(frames)
        self.history: list[VideoFrame] = []
        self.history_copied: list[VideoFrame] = []

    def __iter__(self) -> Iterator[VideoFrame]:
        return self

    def __next__(self) -> VideoFrame:
        frame = next(self.frames)
        self.history.append(frame)
        self.history_copied.append(deepcopy(frame))
        return frame


def _recursive_is_not(x: Any, y: Any) -> None:  # noqa: C901, ANN401
    """Asserts that x and y are not the same mutable object, recursing over sub-elements as appropriate."""
    if not (x is None or isinstance(x, (bool, int, float, complex, str, tuple, frozenset))):
        # Check disabled for immutable types
        assert x is not y

    if isinstance(x, (tuple, list, set)) and isinstance(y, (tuple, list, set)):
        for x_i, y_i in zip(x, y, strict=False):
            _recursive_is_not(x=x_i, y=y_i)

    if isinstance(x, dict) and isinstance(y, dict):
        for key in set(list(x.keys()) + list(y.keys())):
            _recursive_is_not(x=x.get(key, None), y=y.get(key, None))


def perturber_assertions(  # noqa: C901
    perturb: Callable[..., Generator[VideoFrame, None, None]],
    frames: Iterator[VideoFrame],
    expecteds: Iterator[VideoFrame] | None = None,
    **additional_params: Any,
) -> Generator[VideoFrame, None, None]:
    """Test some blanket assertions for perturbers.

    1) All input frames should remain unchanged
    2) Output should not share memory with any input frame
    3) Output images should have the same dtype as input images
    Additionally, if ``expecteds`` is provided
    4) Output should match ``expecteds``

    Args:
        perturb: Interface with which to generate the perturbation.
        frames: Input video frames iterator.
        expecteds: Optional expected output frames iterator for comparison.
        additional_params: Perturber implementation-specific input param-value pairs.
    """
    frames_wrapper = FrameRecorder(frames)

    for perturbed_frame in perturb(frames=frames_wrapper, **additional_params):
        if expecteds is not None:
            # Ensure all outputs match expected values
            try:
                expected = next(expecteds)
                assert np.array_equal(expected.image, perturbed_frame.image)
                assert expected.timestamp == perturbed_frame.timestamp
                assert (expected.boxes is None) == (perturbed_frame.boxes is None)
                if expected.boxes is not None and perturbed_frame.boxes is not None:
                    assert list(expected.boxes) == list(perturbed_frame.boxes)
                assert expected.additional_params == perturbed_frame.additional_params
            except StopIteration as e:
                raise AssertionError("Actual output has more frames than expected") from e

        # Since video perturbers may add or remove frames as part of the perturbation, it is
        # not sufficient to check each perturbed frame for memory sharing against the original
        # frame in the same position - all possible pairs of original and perturbed frames must
        # be checked, regardless of position. Copies of the original frames before passing them
        # to the perturber are also maintained, to ensure no pixel modification was done that
        # affected the original object.
        for prev_frame, prev_frame_copy in zip(frames_wrapper.history, frames_wrapper.history_copied, strict=False):
            assert np.array_equal(prev_frame.image, prev_frame_copy.image)
            assert prev_frame is not perturbed_frame
            if prev_frame.boxes is not None and perturbed_frame.boxes is not None:
                assert prev_frame.boxes is not perturbed_frame.boxes
                for box1, metadata1 in prev_frame.boxes:
                    for box2, metadata2 in perturbed_frame.boxes:
                        assert box1 is not box2
                        _recursive_is_not(x=metadata1, y=metadata2)
            if prev_frame.additional_params is not None:
                _recursive_is_not(x=prev_frame.additional_params, y=perturbed_frame.additional_params)
            assert not np.shares_memory(prev_frame.image, perturbed_frame.image)
            assert prev_frame.image.dtype == perturbed_frame.image.dtype
        yield perturbed_frame

    if expecteds is not None:
        try:
            next(expecteds)
            raise AssertionError("Actual output has fewer frames than expected")
        except StopIteration:
            pass
