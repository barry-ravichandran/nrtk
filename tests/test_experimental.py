"""Tests for nrtk's experimental feature gate (nrtk._experimental)."""

import warnings
from unittest.mock import patch

import pytest

import nrtk.interfaces
from nrtk import _experimental


@pytest.mark.core
def test_require_raises_when_disabled() -> None:
    # Conftest enables experimental for the whole suite, so turn it off here to hit the disabled path.
    with (
        patch("nrtk._experimental.enabled", new=False),
        pytest.raises(ImportError, match="import nrtk.experimental"),
    ):
        _experimental.require("nrtk.interfaces.PerturbVideo")


@pytest.mark.core
def test_warns_once_on_first_use() -> None:
    # First touch warns; after that it's quiet.
    name = "nrtk.interfaces._WarnOnceProbe"
    _experimental._warned.discard(name)
    with pytest.warns(_experimental.ExperimentalWarning, match="experimental"):
        _experimental.require(name)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _experimental.require(name)  # already warned, so it stays silent


@pytest.mark.core
def test_interface_gate_raises_when_disabled() -> None:
    # Importing an experimental name from its stable location fails until experimental is enabled.
    with (
        patch("nrtk._experimental.enabled", new=False),
        pytest.raises(ImportError, match="import nrtk.experimental"),
    ):
        nrtk.interfaces.__getattr__("PerturbVideo")


@pytest.mark.core
def test_interface_gate_rejects_unknown_name() -> None:
    # Names that aren't enrolled fall through to a normal AttributeError.
    with pytest.raises(AttributeError, match="has no attribute"):
        nrtk.interfaces.__getattr__("NotARealInterface")
