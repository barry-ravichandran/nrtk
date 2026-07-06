"""Mixin providing shared tests for PerturbVideo implementations.

Mirrors tests/impls/perturb_image/perturber_tests_mixin.py for the video domain.

Subclasses must define:
    - ``impl_class``: the PerturbVideo implementation class under test
    - ``make_perturber()``: returns a ready-to-use instance of that class
    - ``make_frames()``: returns a fresh list[VideoFrame] valid for that perturber

Shared Test Cases:
    Plugin Discovery
        - Perturber is discoverable via PerturbVideo.get_impls()
    Iterator Contract
        - perturb() requires an Iterator[VideoFrame]; a plain list raises
          TypeError, while a valid iterator can be consumed, yielding VideoFrames.

Note: this mixin deliberately does NOT assert output frame count == input count;
that is not a universal PerturbVideo contract. Keep any equal-length assertion in
the implementation-specific test class.
"""

from __future__ import annotations

from typing import ClassVar

import pytest

from nrtk.interfaces import PerturbVideo, VideoFrame


class PerturbVideoTestsMixin:
    """Mixin providing shared tests for PerturbVideo implementations."""

    impl_class: ClassVar[type[PerturbVideo]]

    def make_perturber(self) -> PerturbVideo:
        """Return a ready-to-use instance of ``impl_class``."""
        raise NotImplementedError

    def make_frames(self) -> list[VideoFrame]:
        """Return a fresh list of VideoFrame objects valid for the perturber."""
        raise NotImplementedError

    # ========================== Plugin Discovery ==========================

    def test_plugin_discovery(self) -> None:
        """Perturber is discoverable via PerturbVideo.get_impls()."""
        assert self.impl_class in PerturbVideo.get_impls()

    # ========================== Iterator Contract =========================

    def test_perturb_requires_iterator(self) -> None:
        """``perturb`` requires an Iterator[VideoFrame], not a plain list."""
        perturber = self.make_perturber()
        # A plain list is rejected by the iterator contract.
        with pytest.raises(TypeError, match="not an iterator"):
            list(perturber(frames=self.make_frames()))  # type: ignore[arg-type]
        # A valid iterator can be consumed without error and yields VideoFrames.
        outputs = list(perturber(frames=iter(self.make_frames())))
        assert all(isinstance(frame, VideoFrame) for frame in outputs)
