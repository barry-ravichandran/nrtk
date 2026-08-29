import numpy as np

from nrtk.impls.perturb_image.photometric._noise.noise_perturber_mixin import NoisePerturberMixin
from tests.utils import random_image


def seed_assertions(perturber: type[NoisePerturberMixin], seed: int) -> None:
    """Test that output is reproducible if a seed is provided.

    :param perturber: SKImage random_noise perturber class of interest.
    :param seed: Seed value.
    """
    dummy_image_a = random_image()
    dummy_image_b = random_image()

    # Test as seed value
    inst_1 = perturber(seed=seed)
    out_1a, _ = inst_1(image=dummy_image_a)
    out_1b, _ = inst_1(image=dummy_image_b)
    inst_2 = perturber(seed=seed)
    out_2a, _ = inst_2(image=dummy_image_a)
    out_2b, _ = inst_2(image=dummy_image_b)
    assert np.array_equal(out_1a, out_2a)
    assert np.array_equal(out_1b, out_2b)
