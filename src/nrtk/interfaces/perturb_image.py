"""Defines PerturbImage, an interface for implementing algorithms that generate perturbed numpy.ndarray images.

Classes:
    PerturbImage: An abstract base class that specifies the structure for image perturbation
    algorithms, allowing for different perturbation techniques to be implemented.

Dependencies:
    - numpy for handling image arrays.
    - smqtk_core for configurable plugin interface capabilities.

Usage:
    To create a custom image perturbation class, inherit from `PerturbImage` and implement
    the `perturb` method, defining the specific perturbation logic.

Example:
    class CustomPerturbImage(PerturbImage):
        def perturb(self, image, additional_params=None):
            # Custom perturbation logic here
            pass

    perturber = CustomPerturbImage()
    perturbed_image = perturber(image_data)
"""

from __future__ import annotations

import abc
from collections.abc import Hashable, Iterable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from smqtk_core import Plugfigurable
from smqtk_image_io.bbox import AxisAlignedBoundingBox


class PerturbImage(Plugfigurable):
    """Algorithm that generates a perturbed image for given input image stimulus as a ``numpy.ndarray`` type array."""

    def __init__(self, box_alignment_mode: str = "extent") -> None:
        """Initializes the PerturbImage.

        :param box_alignment_mode: Mode for how to handle how bounding boxes change.
            Should be one of the following options:
                extent: a new axis-aligned bounding box that encases the transformed misaligned box
                extant: a new axis-aligned bounding box that is encased inside the transformed misaligned box
                median: median between extent and extant
            Default value is extent
        """
        self.box_alignment_mode = box_alignment_mode

    @abc.abstractmethod
    def perturb(
        self,
        image: np.ndarray[Any, Any],
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None = None,
        additional_params: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray[Any, Any], Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None]:
        """Generate a perturbed image for the given image stimulus.

        Note perturbers that resize, rotate, or similarly affect the dimensions of an image may impact
        scoring if bounding boxes are not similarly transformed.

        :param image: Input image as a numpy array.
        :param boxes: Input bounding boxes as a Iterable of tuples containing bounding boxes. This is the single
            image output from DetectImageObjects.detect_objects
        :param additional_params: A dictionary containing perturber implementation-specific input param-values pairs.

        Returns:
            Perturbed image as numpy array, including matching dtype. Implementations should impart no side
                effects upon the input image.
            Iterable of tuples containing the bounding boxes for detections in the image. If an implementation
                modifies the size of an image, it is expected to modify the bounding boxes as well.
        """
        if additional_params is None:
            additional_params = dict()
        return image, boxes

    def _rescale_boxes(
        self,
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]],
        orig_shape: ArrayLike,
        new_shape: ArrayLike,
    ) -> Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]]:
        """Utility function to rescale set of bounding boxes based on provided old and new image sizes.

        :param boxes: Bounding boxes as input to the ``perturb()`` method.
        :param orig_shape: Original shape of the image that the provided bounding boxes belong to. It is assumed that
            first two members of this represent the height and width respectively.
        :param new_shape: New image shape to scale boxes to. It is assumed that first two members of this represent the
            height and width respectively.

        Returns:
            Rescaled bounding boxes in the same format as input.
        """
        y_factor, x_factor = np.array(new_shape)[0:2] / np.array(orig_shape)[0:2]
        if x_factor == y_factor == 1:
            # no scaling needed
            return boxes

        scaled_boxes = list()
        for box, score_dict in boxes:
            x0, y0 = box.min_vertex
            x1, y1 = box.max_vertex
            scaled_box = AxisAlignedBoundingBox(
                (x0 * x_factor, y0 * y_factor),
                (x1 * x_factor, y1 * y_factor),
            )
            scaled_boxes.append((scaled_box, score_dict))

        return scaled_boxes

    def __call__(
        self,
        image: np.ndarray[Any, Any],
        boxes: Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None = None,
        additional_params: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray[Any, Any], Iterable[tuple[AxisAlignedBoundingBox, dict[Hashable, float]]] | None]:
        """Calls ``perturb()`` with the given input image."""
        if additional_params is None:
            additional_params = dict()
        return self.perturb(image=image, boxes=boxes, additional_params=additional_params)

    @classmethod
    def get_type_string(cls) -> str:
        """Returns the fully qualified type string of the `PerturbImage` class or its subclass.

        Returns:
            A string representing the fully qualified type, in the format `<module>.<class_name>`.
            For example, "my_module.CustomPerturbImage".
        """
        return f"{cls.__module__}.{cls.__name__}"

    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the PerturbImage instance.

        Returns:
            dict[str, Any]: Configuration dictionary with current settings.
        """
        return {"box_alignment_mode": self.box_alignment_mode}
