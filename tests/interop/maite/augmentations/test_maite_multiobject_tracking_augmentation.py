import copy
from collections.abc import Sequence
from fractions import Fraction

import numpy as np
import pytest
from maite.protocols.multiobject_tracking import DatumMetadataType, InputType
from smqtk_image_io.bbox import AxisAlignedBoundingBox

from nrtk.impls.perturb_video import FramewisePerturber
from nrtk.interfaces import PerturbVideo, VideoFrame
from nrtk.interop import MAITEMultiobjectTrackingAugmentation
from nrtk.interop._maite.augmentations._maite_multiobject_tracking_augmentation import (
    MAITEMultiobjectTrackingTarget,
    MAITESingleFrameObjectTrackingTarget,
    MAITEVideoFrame,
)
from tests.fakes import FakeImagePerturber
from tests.interop.maite.perturber_fixtures import ResizePerturber
from tests.utils import random_image


@pytest.mark.maite
class TestMAITEMultiobjectTrackingAugmentation:
    @pytest.mark.parametrize(
        ("data_in", "expected_frame_out", "expected_target_out"),
        [
            (
                VideoFrame(
                    image=np.ones((8, 8, 3), dtype=np.uint8),
                    timestamp=0.0,
                    boxes=[
                        (
                            AxisAlignedBoundingBox(min_vertex=(1.0, 2.0), max_vertex=(3.0, 4.0)),
                            {0: 0.8},
                        ),
                        (
                            AxisAlignedBoundingBox(min_vertex=(2.0, 4.0), max_vertex=(6.0, 8.0)),
                            {2: 0.86},
                        ),
                    ],
                    additional_params={
                        "pts": 0,
                        "frame_index": 0,
                        "track_ids": np.asarray([0, 1]),
                    },
                ),
                MAITEVideoFrame(
                    pixels=np.ones((3, 8, 8), dtype=np.uint8),
                    time_s=0.0,
                    pts=0,
                    frame_index=0,
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]]),
                    labels=np.asarray([0, 2]),
                    scores=np.asarray([0.8, 0.86]),
                    track_ids=np.asarray([0, 1]),
                ),
            ),
            (
                VideoFrame(
                    image=np.zeros((8, 16, 3), dtype=np.uint8),
                    timestamp=0.0,
                    boxes=[
                        (
                            AxisAlignedBoundingBox(min_vertex=(1.0, 5.0), max_vertex=(3.0, 10.0)),
                            {3: 0.35},
                        ),
                    ],
                    additional_params={
                        "pts": 0,
                        "frame_index": 0,
                        "track_ids": np.asarray([-1]),
                    },
                ),
                MAITEVideoFrame(
                    pixels=np.zeros((3, 8, 16), dtype=np.uint8),
                    time_s=0.0,
                    pts=0,
                    frame_index=0,
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[1.0, 5.0, 3.0, 10.0]]),
                    labels=np.asarray([3]),
                    scores=np.asarray([0.35]),
                    track_ids=np.asarray([-1]),
                ),
            ),
            (
                VideoFrame(
                    image=np.zeros((8, 16, 3), dtype=np.uint8),
                    timestamp=0.0,
                    boxes=None,
                    additional_params={
                        "pts": 0,
                        "frame_index": 0,
                        "track_ids": np.empty((0,)),
                    },
                ),
                MAITEVideoFrame(
                    pixels=np.zeros((3, 8, 16), dtype=np.uint8),
                    time_s=0.0,
                    pts=0,
                    frame_index=0,
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.empty((0, 4)),
                    labels=np.empty((0,)),
                    scores=np.empty((0, 0)),
                    track_ids=np.empty((0,)),
                ),
            ),
        ],
    )
    def test_nrtk_to_maite_frame(
        self,
        data_in: VideoFrame,
        expected_frame_out: MAITEVideoFrame,
        expected_target_out: MAITESingleFrameObjectTrackingTarget,
    ) -> None:
        frame_out, target_out = MAITEMultiobjectTrackingAugmentation._nrtk_to_maite_frame(data_in)

        assert np.allclose(frame_out.pixels, expected_frame_out.pixels)
        assert np.isclose(frame_out.time_s, expected_frame_out.time_s)
        assert frame_out.pts == expected_frame_out.pts
        assert frame_out.frame_index == expected_frame_out.frame_index

        assert np.allclose(target_out.boxes, expected_target_out.boxes)
        assert np.allclose(target_out.labels, expected_target_out.labels)
        assert np.allclose(target_out.scores, expected_target_out.scores)
        assert np.allclose(target_out.track_ids, expected_target_out.track_ids)

    @pytest.mark.parametrize(
        ("frame_in", "target_in", "expected_frame_out"),
        [
            (
                MAITEVideoFrame(
                    pixels=np.ones((3, 8, 8), dtype=np.uint8),
                    time_s=0.0,
                    pts=0,
                    frame_index=0,
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]]),
                    labels=np.asarray([0, 2]),
                    scores=np.asarray([0.8, 0.86]),
                    track_ids=np.asarray([0, 1]),
                ),
                VideoFrame(
                    image=np.ones((8, 8, 3), dtype=np.uint8),
                    timestamp=0.0,
                    boxes=[
                        (
                            AxisAlignedBoundingBox(min_vertex=(1.0, 2.0), max_vertex=(3.0, 4.0)),
                            {0: 0.8},
                        ),
                        (
                            AxisAlignedBoundingBox(min_vertex=(2.0, 4.0), max_vertex=(6.0, 8.0)),
                            {2: 0.86},
                        ),
                    ],
                    additional_params={
                        "pts": 0,
                        "frame_index": 0,
                        "track_ids": np.asarray([0, 1]),
                    },
                ),
            ),
            (
                MAITEVideoFrame(
                    pixels=np.zeros((3, 8, 16), dtype=np.uint8),
                    time_s=0.0,
                    pts=0,
                    frame_index=0,
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[1.0, 5.0, 3.0, 10.0]]),
                    labels=np.asarray([3]),
                    scores=np.asarray([0.35]),
                    track_ids=np.asarray([-1]),
                ),
                VideoFrame(
                    image=np.zeros((8, 16, 3), dtype=np.uint8),
                    timestamp=0.0,
                    boxes=[
                        (
                            AxisAlignedBoundingBox(min_vertex=(1.0, 5.0), max_vertex=(3.0, 10.0)),
                            {3: 0.35},
                        ),
                    ],
                    additional_params={
                        "pts": 0,
                        "frame_index": 0,
                        "track_ids": np.asarray([-1]),
                    },
                ),
            ),
        ],
    )
    def test_maite_to_nrtk_frame(
        self,
        frame_in: MAITEVideoFrame,
        target_in: MAITESingleFrameObjectTrackingTarget,
        expected_frame_out: VideoFrame,
    ) -> None:
        frame_out = MAITEMultiobjectTrackingAugmentation._maite_to_nrtk_frame(
            frame=frame_in,
            single_frame_target=target_in,
        )

        assert np.allclose(frame_out.image, expected_frame_out.image)
        assert np.isclose(frame_out.timestamp, expected_frame_out.timestamp)
        for targets, expected_targets in zip(frame_out.boxes, expected_frame_out.boxes, strict=True):
            assert targets[0] == expected_targets[0]  # AxisAlignedBoundingBoxes
            assert targets[1] == expected_targets[1]  # Confidence scores
        assert frame_out.additional_params.keys() == expected_frame_out.additional_params.keys()
        assert frame_out.additional_params["pts"] == expected_frame_out.additional_params["pts"]
        assert frame_out.additional_params["frame_index"] == expected_frame_out.additional_params["frame_index"]
        assert np.allclose(frame_out.additional_params["track_ids"], expected_frame_out.additional_params["track_ids"])

    @pytest.mark.parametrize(
        ("perturber", "nrtk_vid_in", "vid_in", "targets_in", "expected_targets_out"),
        [
            (
                FramewisePerturber(FakeImagePerturber()),
                [
                    VideoFrame(
                        image=np.ones((8, 16, 3), dtype=np.uint8),
                        timestamp=0.0,
                        boxes=[
                            (
                                AxisAlignedBoundingBox(min_vertex=(1.0, 5.0), max_vertex=(3.0, 10.0)),
                                {3: 0.35},
                            ),
                        ],
                        additional_params={
                            "pts": 0,
                            "frame_index": 0,
                            "track_ids": np.asarray([0]),
                        },
                    ),
                    VideoFrame(
                        image=np.ones((8, 16, 3), dtype=np.uint8),
                        timestamp=1.0,
                        boxes=[
                            (
                                AxisAlignedBoundingBox(min_vertex=(2.0, 6.0), max_vertex=(4.0, 11.0)),
                                {3: 0.48},
                            ),
                        ],
                        additional_params={
                            "pts": 1,
                            "frame_index": 1,
                            "track_ids": np.asarray([0]),
                        },
                    ),
                ],
                [
                    MAITEVideoFrame(pixels=np.ones((3, 8, 16), dtype=np.uint8), time_s=0.0, pts=0, frame_index=0),
                    MAITEVideoFrame(pixels=np.ones((3, 8, 16), dtype=np.uint8), time_s=1.0, pts=1, frame_index=1),
                ],
                MAITEMultiobjectTrackingTarget(
                    frame_tracks=[
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[1.0, 5.0, 3.0, 10.0]]),
                            labels=np.asarray([3]),
                            scores=np.asarray([0.35]),
                            track_ids=np.asarray([0]),
                        ),
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[2.0, 6.0, 4.0, 11.0]]),
                            labels=np.asarray([3]),
                            scores=np.asarray([0.48]),
                            track_ids=np.asarray([0]),
                        ),
                    ],
                ),
                MAITEMultiobjectTrackingTarget(
                    frame_tracks=[
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[1.0, 5.0, 3.0, 10.0]]),
                            labels=np.asarray([3]),
                            scores=np.asarray([0.35]),
                            track_ids=np.asarray([0]),
                        ),
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[2.0, 6.0, 4.0, 11.0]]),
                            labels=np.asarray([3]),
                            scores=np.asarray([0.48]),
                            track_ids=np.asarray([0]),
                        ),
                    ],
                ),
            ),
            (
                FramewisePerturber(ResizePerturber(w=4, h=16)),
                [
                    VideoFrame(
                        image=np.zeros((8, 8, 3), dtype=np.uint8),
                        timestamp=0.0,
                        boxes=[
                            (
                                AxisAlignedBoundingBox(min_vertex=(1.0, 5.0), max_vertex=(3.0, 6.0)),
                                {3: 0.35},
                            ),
                        ],
                        additional_params={
                            "pts": 0,
                            "frame_index": 0,
                            "track_ids": np.asarray([0]),
                        },
                    ),
                ],
                [
                    MAITEVideoFrame(pixels=np.zeros((3, 8, 8), dtype=np.uint8), time_s=0.0, pts=0, frame_index=0),
                ],
                MAITEMultiobjectTrackingTarget(
                    frame_tracks=[
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[1.0, 5.0, 3.0, 6.0]]),
                            labels=np.asarray([2]),
                            scores=np.asarray([0.79]),
                            track_ids=np.asarray([3]),
                        ),
                    ],
                ),
                MAITEMultiobjectTrackingTarget(
                    frame_tracks=[
                        MAITESingleFrameObjectTrackingTarget(
                            boxes=np.asarray([[0.5, 10.0, 1.5, 12.0]]),
                            labels=np.asarray([2]),
                            scores=np.asarray([0.79]),
                            track_ids=np.asarray([3]),
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_augmentation_adapter(
        self,
        perturber: PerturbVideo,
        nrtk_vid_in: Sequence[VideoFrame],
        vid_in: InputType,
        targets_in: MAITEMultiobjectTrackingTarget,
        expected_targets_out: MAITEMultiobjectTrackingTarget,
    ) -> None:
        """Test that the augmentation adapter functions appropriately.

        Tests that the adapter generates the same perturbation result as the
        core perturber and that bboxes and metadata are appropriately updated.
        """
        augmentation = MAITEMultiobjectTrackingAugmentation(augment=perturber, augment_id="test_augment")
        # Metadata is unused, just need to make sure it's passed through
        md_in: DatumMetadataType = {"id": 1, "height": 8, "width": 16, "time_base": Fraction("1/60"), "size": 1024}

        # Get copies to check for modification
        vid_copy = copy.deepcopy(vid_in)
        targets_copy = copy.deepcopy(targets_in)
        md_copy = copy.deepcopy(md_in)

        # Get expected image and metadata from "normal" perturber
        expected_video_out = perturber(frames=iter(nrtk_vid_in))
        expected_md_out = dict(md_in)
        expected_md_out["nrtk_perturber_config"] = [perturber.get_config()]

        # Apply augmentation via adapter
        frames_out, targets_out, md_out = augmentation(([vid_in], [targets_in], [md_in]))

        # Check that expectations hold
        for frame_out, expected_frame in zip(frames_out[0], expected_video_out, strict=True):
            assert np.array_equal(frame_out.pixels, np.transpose(expected_frame.image, (2, 0, 1)))
        assert len(targets_out[0].frame_tracks) == len(expected_targets_out.frame_tracks)
        for expected_tgt, tgt_out in zip(expected_targets_out.frame_tracks, targets_out[0].frame_tracks, strict=True):
            assert np.array_equal(expected_tgt.boxes, tgt_out.boxes)
            assert np.array_equal(expected_tgt.labels, tgt_out.labels)
            assert np.array_equal(expected_tgt.scores, tgt_out.scores)
            assert np.array_equal(expected_tgt.track_ids, tgt_out.track_ids)
        assert md_out[0] == expected_md_out

        # Check that input data was not modified
        for frame_in, frame_copy in zip(vid_in, vid_copy, strict=True):
            assert np.allclose(frame_in.pixels, frame_copy.pixels)
            assert np.isclose(frame_in.time_s, frame_copy.time_s)
            assert frame_in.pts == frame_copy.pts
            assert frame_in.frame_index == frame_copy.frame_index
        assert len(targets_copy.frame_tracks) == len(targets_in.frame_tracks)
        for tgt_in, tgt_copy in zip(targets_in.frame_tracks, targets_copy.frame_tracks, strict=True):
            assert np.array_equal(tgt_in.boxes, tgt_copy.boxes)
            assert np.array_equal(tgt_in.labels, tgt_copy.labels)
            assert np.array_equal(tgt_in.scores, tgt_copy.scores)
            assert np.array_equal(tgt_in.track_ids, tgt_copy.track_ids)
        assert md_in == md_copy

    @pytest.mark.parametrize(
        ("perturbers"),
        [
            [FramewisePerturber(FakeImagePerturber()), FramewisePerturber(ResizePerturber(w=64, h=512))],
        ],
    )
    def test_multiple_augmentations(
        self,
        perturbers: Sequence[PerturbVideo],
    ) -> None:
        """Test that the adapter appends, not overrides nrtk configs when multiple perturbations are applied."""
        vid_in = [
            MAITEVideoFrame(pixels=random_image(size=(3, 256, 256)), time_s=0.0, pts=0, frame_index=0),
            MAITEVideoFrame(pixels=random_image(size=(3, 256, 256)), time_s=1.0, pts=1, frame_index=1),
        ]
        targets_in = MAITEMultiobjectTrackingTarget(
            frame_tracks=[
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[1.0, 5.0, 3.0, 10.0]]),
                    labels=np.asarray([3]),
                    scores=np.asarray([0.35]),
                    track_ids=np.asarray([0]),
                ),
                MAITESingleFrameObjectTrackingTarget(
                    boxes=np.asarray([[2.0, 6.0, 4.0, 11.0]]),
                    labels=np.asarray([3]),
                    scores=np.asarray([0.48]),
                    track_ids=np.asarray([0]),
                ),
            ],
        )
        # Metadata is unused for this test, just need it for required input
        md_in: DatumMetadataType = {"id": 1, "height": 256, "width": 256, "time_base": Fraction("1/60"), "size": 1024}

        # Iteratively apply perturbers
        vids_out = [vid_in]
        targets_out = [targets_in]
        md_out = [md_in]
        for p_idx, perturber in enumerate(perturbers):
            augmentation = MAITEMultiobjectTrackingAugmentation(augment=perturber, augment_id=f"test_augment_{p_idx}")
            vids_out, targets_out, md_out = augmentation((vids_out, targets_out, md_out))

        assert "nrtk_perturber_config" in md_out[0]
        all_perturber_configs = [perturber.get_config() for perturber in perturbers]
        assert md_out[0].get("nrtk_perturber_config") == all_perturber_configs
