import logging
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from datamaite import BoxAnnotation, BoxTrackDataset, Task, VideoSequence
from smqtk_image_io.bbox import AxisAlignedBoundingBox
from typing_extensions import override

from nrtk.entrypoints._nrtk_eo._nrtk_eo_video_perturber import nrtk_eo_video_perturber
from nrtk.interfaces import PerturbFactory, VideoFrame
from tests.fakes import FakeImagePerturber, FakePerturbFactory, FakeVideoPerturber
from tests.impls import INPUT_DRONE_VIDEO_FILE_PATH

_CATEGORY_URI = "http://example.com/ontology/CAR"
LOGGER = "nrtk.entrypoints._nrtk_eo._nrtk_eo_video_perturber"
SHIFT = (10.0, 20.0)
TRACKS: dict[int, tuple[float, float, float, float]] = {
    1: (10.0, 20.0, 30.0, 40.0),
    2: (50.0, 60.0, 8.0, 6.0),
}


class _BoxDroppingVideoPerturber(FakeVideoPerturber):
    """Drops the last box of every frame."""

    @override
    def perturb(self, *, frames: Iterator[VideoFrame], **_: Any) -> Generator[VideoFrame, None, None]:
        for frame in frames:
            yield VideoFrame(
                image=np.copy(frame.image),
                timestamp=frame.timestamp,
                boxes=list(frame.boxes)[:-1],
                additional_params=dict(frame.additional_params),
            )


class _ShiftingVideoPerturber(FakeVideoPerturber):
    """Translates every box by SHIFT so the xyxy->xywh inverse is observable."""

    @override
    def perturb(self, *, frames: Iterator[VideoFrame], **_: Any) -> Generator[VideoFrame, None, None]:
        for frame in frames:
            shift: tuple[float, float] = tuple(frame.additional_params.get("shift", SHIFT))
            shifted = [
                (
                    AxisAlignedBoundingBox(
                        min_vertex=np.asarray(bbox.min_vertex) + shift,
                        max_vertex=np.asarray(bbox.max_vertex) + shift,
                    ),
                    dict(meta),
                )
                for bbox, meta in frame.boxes
            ]
            yield VideoFrame(
                image=np.copy(frame.image),
                timestamp=frame.timestamp,
                boxes=shifted,
                additional_params=dict(frame.additional_params),
            )


def _make_mot_dataset(num_annotated_frames: int = 3) -> BoxTrackDataset:
    """Build a datamaite box-track dataset around the drone test clip."""
    boxes = [
        BoxAnnotation(
            track_uuid=f"0-{track_id}",
            track_id=track_id,
            category_id=1,
            category_uri=_CATEGORY_URI,
            category_name="CAR",
            bbox=bbox,
            attributes={"source": "synthetic"},
            frame_index=frame,
            timestamp=frame / 30.0,
        )
        for frame in range(num_annotated_frames)
        for track_id, bbox in TRACKS.items()
    ]
    seq = VideoSequence(
        video_id=0,
        video_path=INPUT_DRONE_VIDEO_FILE_PATH,
        fps=30.0,
        num_frames=150,
        duration=150 / 30.0,
        annotation_path="synthetic",
        boxes=boxes,
        width=960,
        height=540,
        num_frames_exact=True,
    )
    return BoxTrackDataset(sequences=(seq,), categories={_CATEGORY_URI: 1})


@pytest.mark.maite
@pytest.mark.tools
class TestNRTKEOVideoPerturber:
    @pytest.mark.parametrize(
        ("perturber_factory", "img_dirs"),
        [
            (
                FakePerturbFactory(
                    perturber=FakeVideoPerturber,
                    theta_key="param1",
                    theta_values=[1, 3],
                ),
                ["_param1-1", "_param1-3"],
            ),
            (
                FakePerturbFactory(
                    perturber=FakeImagePerturber,
                    theta_key="param1",
                    theta_values=[1, 3],
                ),
                ["_param1-1", "_param1-3"],
            ),
        ],
    )
    def test_nrtk_eo_video_perturber(
        self,
        perturber_factory: PerturbFactory,
        img_dirs: list[str],
        tmp_path: Path,
    ) -> None:
        """Perturber yields one datamaite MOT dataset per parameter combination."""
        num_annotated_frames = 3
        dataset = _make_mot_dataset(num_annotated_frames=num_annotated_frames)

        augmented_datasets = list(
            nrtk_eo_video_perturber(
                dataset=dataset,
                perturber_factory=perturber_factory,
                staging_dir=str(tmp_path),
            ),
        )

        assert len(augmented_datasets) == len(img_dirs)
        for perturber_params, aug_dataset in augmented_datasets:
            assert perturber_params in img_dirs
            assert isinstance(aug_dataset, BoxTrackDataset)
            assert aug_dataset.task == Task.MOT
            assert len(aug_dataset) == 1

            seq = aug_dataset.sequences[0]
            assert seq.video_path is not None
            assert Path(seq.video_path).exists()
            assert seq.num_frames == dataset.sequences[0].num_frames
            assert aug_dataset.num_boxes == num_annotated_frames * len(TRACKS)
            assert aug_dataset.categories == {_CATEGORY_URI: 1}
            by_key = {(box.frame_index, box.track_id): box for box in seq.boxes}
            for frame in range(num_annotated_frames):
                for track_id, bbox in TRACKS.items():
                    box = by_key[(frame, track_id)]
                    assert box.bbox == bbox
                    assert box.track_uuid == f"0-{track_id}"
                    assert box.category_name == "CAR"
                    assert box.attributes == {"source": "synthetic"}

    def test_shifted_boxes_convert_xyxy_to_xywh(self, tmp_path: Path) -> None:
        """A translating perturber moves the origin and preserves width/height."""
        dataset = _make_mot_dataset()
        perturb_factory = FakePerturbFactory(
            perturber=_ShiftingVideoPerturber,
            theta_key="param1",
            theta_values=[1, 3],
        )

        _, augmented_datasets = list(
            nrtk_eo_video_perturber(
                dataset=dataset,
                perturber_factory=perturb_factory,
                staging_dir=str(tmp_path),
            ),
        )[0]

        for box in augmented_datasets.sequences[0].boxes:
            x, y, w, h = TRACKS[box.track_id]
            assert box.bbox == (x + SHIFT[0], y + SHIFT[1], w, h)

    def test_dropped_boxes_are_rebuilt_with_warning(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """When a perturber drops boxes, that frame's survivors are rebuilt untracked and the user is warned once."""
        dataset = _make_mot_dataset()
        perturb_factory = FakePerturbFactory(
            perturber=_BoxDroppingVideoPerturber,
            theta_key="param1",
            theta_values=[1],
        )

        with caplog.at_level(logging.WARNING, logger=LOGGER):
            _, augmented_datasets = list(
                nrtk_eo_video_perturber(
                    dataset=dataset,
                    perturber_factory=perturb_factory,
                    staging_dir=str(tmp_path),
                ),
            )[0]

        seq = augmented_datasets.sequences[0]
        assert len(seq.boxes) == 3  # one box per annotated frame
        for box in seq.boxes:
            assert box.bbox == TRACKS[1]  # the first box on each frame is the one kept
            assert box.track_id == -1
            assert box.track_uuid.startswith("untracked-")
            assert box.category_id == 1
            assert box.category_name == "CAR"
            assert box.category_uri == _CATEGORY_URI
            assert box.attributes == {}

        messages = [rec.message for rec in caplog.records if "box count changed" in rec.message]
        assert len(messages) == 1
        assert "3 frame(s)" in messages[0]
        assert "3 box(es)" in messages[0]

    def test_annotation_free_video(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """A video with no boxes streams every frame and produces an empty-but-valid sequence, without warnings."""
        dataset = _make_mot_dataset(num_annotated_frames=0)
        perturb_factory = FakePerturbFactory(
            perturber=FakeVideoPerturber,
            theta_key="param1",
            theta_values=[1],
        )

        with caplog.at_level(logging.WARNING, logger=LOGGER):
            _, augmented_datasets = list(
                nrtk_eo_video_perturber(
                    dataset=dataset,
                    perturber_factory=perturb_factory,
                    staging_dir=str(tmp_path),
                ),
            )[0]

        seq = augmented_datasets.sequences[0]
        assert seq.num_frames == 150
        assert seq.boxes == []
        assert seq.video_path is not None
        assert Path(seq.video_path).exists()
        assert not [rec for rec in caplog.records if "box count changed" in rec.message]

    def test_metadata_reaches_perturber(self, tmp_path: Path) -> None:
        """Datum metadata is merged per image id and forwarded to the perturber as kwargs."""
        dataset = _make_mot_dataset()
        shift = (7.0, 11.0)

        _, augmented_datasets = next(
            iter(
                nrtk_eo_video_perturber(
                    dataset=dataset,
                    perturber_factory=FakePerturbFactory(
                        perturber=_ShiftingVideoPerturber,
                        theta_key="param1",
                        theta_values=[1],
                    ),
                    metadata={0: {"shift": shift}},
                    staging_dir=str(tmp_path),
                ),
            ),
        )

        for box in augmented_datasets.sequences[0].boxes:
            x, y, w, h = TRACKS[box.track_id]
            assert box.bbox == (x + shift[0], y + shift[1], w, h)
