"""Defines FramewisePerturber to apply a PerturbImage instance to each frame independently.

Classes:
    FramewisePerturber: A perturbation class for applying an image perturber to each frame of a video.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from copy import deepcopy
from typing import Any

from smqtk_core.configuration import from_config_dict, to_config_dict
from typing_extensions import Self, override

from nrtk.impls.perturb_image._nop_perturber import _NOPPerturber as NOPPerturber
from nrtk.interfaces import PerturbImage, PerturbVideo, VideoFrame
from nrtk.interfaces._perturb_video import _perturb_guard


class FramewisePerturber(PerturbVideo):
    """Applies an image perturbation to each frame of an input video.

    Attributes:
        frame_perturber: PerturbImage:
            Perturber to apply to each frame.
    """

    def __init__(self, frame_perturber: PerturbImage | None = None) -> None:
        """Initializes the FramewisePerturber.

        Args:
            frame_perturber:
                Perturber to apply to each frame.
        """
        super().__init__()

        if frame_perturber is None:
            frame_perturber = NOPPerturber()

        self.frame_perturber = frame_perturber

    @override
    @_perturb_guard
    def perturb(
        self,
        *,
        frames: Iterator[VideoFrame],
        **kwargs: Any,
    ) -> Generator[VideoFrame, None, None]:
        """Apply the perturber to each frame of the input video.

        Args:
            frames:
                Iterator over input video frames. Pass ``iter(my_list)``
                to feed a list.
            kwargs:
                Additional parameters for perturbation (not used).

        Returns:
            :return Generator[VideoFrame, None, None]:
                A generator which produces perturbed video frames.
        """
        for frame in frames:
            frame_params: dict[str, Any] = {} if frame.additional_params is None else frame.additional_params
            perturbed_image, perturbed_boxes = self.frame_perturber(
                image=frame.image,
                boxes=frame.boxes,
                **frame_params,
            )
            yield VideoFrame(
                image=perturbed_image,
                timestamp=frame.timestamp,
                boxes=perturbed_boxes,
                additional_params=deepcopy(frame_params),
            )

    @override
    def get_config(self) -> dict[str, Any]:
        """Get the configuration dictionary of the FramewisePerturber instance.

        Returns:
            :return dict[str, Any]: Configuration dictionary containing perturber configurations.
        """
        cfg = super().get_config()
        cfg["frame_perturber"] = to_config_dict(self.frame_perturber)
        return cfg

    @override
    @classmethod
    def from_config(
        cls,
        config_dict: dict[str, Any],
        merge_default: bool = True,
    ) -> Self:
        """Create a FramewisePerturber instance from a configuration dictionary.

        Args:
            config_dict:
                Configuration dictionary with perturber details.
            merge_default:
                Whether to merge with the default configuration.

        Returns:
            :return FramewisePerturber: An instance of FramewisePerturber.
        """
        config_dict = dict(config_dict)

        config_dict["frame_perturber"] = from_config_dict(
            config=config_dict["frame_perturber"],
            type_iter=PerturbImage.get_impls(),
        )

        return super().from_config(config_dict, merge_default=merge_default)
