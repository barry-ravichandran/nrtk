import copy
from collections.abc import Sequence

import numpy as np
import pytest
from maite.protocols.object_detection import DatumMetadataType, TargetType

from nrtk.interfaces import PerturbImage
from nrtk.interop import MAITEObjectDetectionAugmentation
from nrtk.interop._maite.datasets import MAITEObjectDetectionTarget
from tests.fakes import FakeDeviceTensor, FakeImagePerturber
from tests.interop.maite.perturber_fixtures import ResizePerturber
from tests.utils import random_image


@pytest.mark.maite
class TestMAITEObjectDetectionAugmentation:
    @pytest.mark.parametrize(
        ("perturber", "targets_in", "expected_targets_out"),
        [
            (
                FakeImagePerturber(),
                [
                    MAITEObjectDetectionTarget(
                        boxes=np.asarray([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]]),
                        labels=np.asarray([0, 2]),
                        scores=np.asarray([0.8, 0.86]),
                    ),
                ],
                [
                    MAITEObjectDetectionTarget(
                        boxes=np.asarray([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]]),
                        labels=np.asarray([0, 2]),
                        scores=np.asarray([0.8, 0.86]),
                    ),
                ],
            ),
            (
                ResizePerturber(w=64, h=512),
                [
                    MAITEObjectDetectionTarget(
                        boxes=np.asarray([[4.0, 8.0, 16.0, 32.0], [2.0, 4.0, 6.0, 8.0]]),
                        labels=np.asarray([1, 5]),
                        scores=np.asarray([0.8, 0.86]),
                    ),
                ],
                [
                    MAITEObjectDetectionTarget(
                        boxes=np.asarray([[1.0, 16.0, 4.0, 64.0], [0.5, 8.0, 1.5, 16.0]]),
                        labels=np.asarray([1, 5]),
                        scores=np.asarray([0.8, 0.86]),
                    ),
                ],
            ),
        ],
        ids=["no-op perturber", "resize"],
    )
    def test_augmentation_adapter(
        self,
        perturber: PerturbImage,
        targets_in: Sequence[TargetType],  # pyright: ignore [reportInvalidTypeForm]
        expected_targets_out: Sequence[TargetType],  # pyright: ignore [reportInvalidTypeForm]
    ) -> None:
        """Test that the augmentation adapter functions appropriately.

        Tests that the adapter generates the same image perturbation result
        as the core perturber and that bboxes and metadata are appropriately
        updated.
        """
        augmentation = MAITEObjectDetectionAugmentation(augment=perturber, augment_id="test_augment")
        img_in = random_image(size=(3, 256, 256))
        md_in: list[DatumMetadataType] = [{"id": 1}]  # pyright: ignore [reportInvalidTypeForm]

        # Get copies to check for modification
        img_copy = np.copy(img_in)
        targets_copy = copy.deepcopy(targets_in)
        md_copy = copy.deepcopy(md_in)

        # Get expected image and metadata from "normal" perturber
        expected_img_out, _ = perturber(image=np.transpose(img_in, (1, 2, 0)))
        # switch from channel last to channel first
        expected_img_out = np.transpose(expected_img_out, (2, 0, 1))
        expected_md_out = dict(md_in[0])
        expected_md_out["nrtk_perturber_config"] = [perturber.get_config()]

        # Apply augmentation via adapter
        imgs_out, targets_out, md_out = augmentation(([img_in], targets_in, md_in))

        # Check that expectations hold
        assert np.array_equal(imgs_out[0], expected_img_out)
        assert len(targets_out) == len(expected_targets_out)
        for expected_tgt, tgt_out in zip(expected_targets_out, targets_out, strict=False):
            assert np.array_equal(expected_tgt.boxes, tgt_out.boxes)
            assert np.array_equal(expected_tgt.labels, tgt_out.labels)
            assert np.array_equal(expected_tgt.scores, tgt_out.scores)
        assert md_out[0] == expected_md_out

        # Check that input data was not modified
        assert np.array_equal(img_in, img_copy)
        assert len(targets_copy) == len(targets_in)
        for tgt_copy, tgt_in in zip(targets_copy, targets_in, strict=False):
            assert np.array_equal(tgt_copy.boxes, tgt_in.boxes)
            assert np.array_equal(tgt_copy.labels, tgt_in.labels)
            assert np.array_equal(tgt_copy.scores, tgt_in.scores)
        assert md_in == md_copy

    @pytest.mark.parametrize(
        ("perturbers", "targets_in"),
        [
            (
                [FakeImagePerturber(), ResizePerturber(w=64, h=512)],
                [
                    MAITEObjectDetectionTarget(
                        boxes=np.asarray([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]]),
                        labels=np.asarray([0, 2]),
                        scores=np.asarray([0.8, 0.86]),
                    ),
                ],
            ),
        ],
    )
    def test_multiple_augmentations(
        self,
        perturbers: Sequence[PerturbImage],
        targets_in: Sequence[TargetType],
    ) -> None:
        """Test that the adapter appends, not overrides nrtk configs when multiple perturbations are applied."""
        img_in = random_image(size=(3, 256, 256))  # MAITE is channels-first
        md_in: list[DatumMetadataType] = [{"id": 1}]

        imgs_out = [img_in]
        targets_out = targets_in
        md_out = md_in
        for p_idx, perturber in enumerate(perturbers):
            augmentation = MAITEObjectDetectionAugmentation(augment=perturber, augment_id=f"test_augment_{p_idx}")
            imgs_out, targets_out, md_out = augmentation((imgs_out, targets_out, md_out))

        assert "nrtk_perturber_config" in md_out[0]
        all_perturber_configs = [perturber.get_config() for perturber in perturbers]
        assert md_out[0].get("nrtk_perturber_config") == all_perturber_configs

    def test_device_tensor_batch(self) -> None:
        """Test that batch elements which cannot convert directly are still augmented.

        Regression test: the adapter used to call ``np.asarray`` straight on the
        batch elements, which raises for a tensor still on an accelerator. A CPU
        tensor cannot catch that -- it converts fine -- so this fakes the device.
        """
        augmentation = MAITEObjectDetectionAugmentation(augment=FakeImagePerturber(), augment_id="test_augment")

        pixels = np.arange(3 * 16 * 16, dtype=np.uint8).reshape((3, 16, 16))
        target = MAITEObjectDetectionTarget(
            boxes=FakeDeviceTensor(np.asarray([[1.0, 2.0, 3.0, 4.0]])),  # pyright: ignore [reportArgumentType]
            labels=FakeDeviceTensor(np.asarray([0])),  # pyright: ignore [reportArgumentType]
            scores=FakeDeviceTensor(np.asarray([0.8])),  # pyright: ignore [reportArgumentType]
        )

        imgs_out, targets_out, _ = augmentation(([FakeDeviceTensor(pixels)], [target], [{"id": 0}]))

        assert isinstance(imgs_out[0], np.ndarray)
        assert np.array_equal(imgs_out[0], pixels)
        assert np.allclose(np.asarray(targets_out[0].boxes), np.asarray([[1.0, 2.0, 3.0, 4.0]]))

    def test_perturber_cannot_write_through_to_input(self) -> None:
        """Test that a perturber writing in place cannot reach the caller's image."""
        augmentation = MAITEObjectDetectionAugmentation(
            augment=FakeImagePerturber(in_place_fill=0),
            augment_id="test_augment",
        )

        image = np.full((3, 4, 4), 7, dtype=np.uint8)
        target = MAITEObjectDetectionTarget(
            boxes=np.asarray([[1.0, 2.0, 3.0, 4.0]]),
            labels=np.asarray([0]),
            scores=np.asarray([0.8]),
        )

        augmentation(([image], [target], [{"id": 0}]))

        assert np.array_equal(image, np.full((3, 4, 4), 7, dtype=np.uint8))
