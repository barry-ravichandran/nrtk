from typing import Any
from typing import Dict
from typing import Hashable
from typing import List
from typing import Tuple

from smqtk_image_io.bbox import AxisAlignedBoundingBox

from nrtk.interfaces.score_detection import ScoreDetection


class NOPScorer(ScoreDetection):
    """
    Example implementation of the ``ScoreDetection`` interface. An instance
    of this class acts as a functor to generate scores for a specific metric
    based on a given set of ground truth and predicted detections.

    This class, in particular, serves as a pass-through "no operation" (NOP)
    scorer.
    """
    def score(
        self,
        actual: List[List[Tuple[AxisAlignedBoundingBox, str]]],
        predicted: List[List[Tuple[AxisAlignedBoundingBox, Dict[Hashable, float]]]]
    ) -> List[float]:
        """
        Return list of zeros equal to the length of the ground truth input.
        """
        if len(actual) != len(predicted):
            raise Exception("Size mismatch between actual and predicted data")
        for actual_det in actual:
            if len(actual_det) < 1:
                raise Exception("Actual bounding boxes must have detections and can't be empty.")

        return [0 for actual_det in actual]

    def get_config(self) -> Dict[str, Any]:
        return {}