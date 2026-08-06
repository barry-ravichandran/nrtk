"""Tests for nrtk's experimental feature gate (nrtk._experimental)."""

import importlib
import warnings
from unittest.mock import patch

import pytest

import nrtk.experimental
import nrtk.interfaces
from nrtk import _experimental

# Matches tests/test_guard.py. `require` never resolves the name it is given -- it only
# echoes it into the error message -- so these tests pass one that does not exist, rather
# than tying the gate's own tests to whichever symbols happen to be experimental today.
FAKE_MODULE = "nrtk.fake_module"


@pytest.mark.core
def test_require_raises_when_disabled() -> None:
    # Conftest enables experimental for the whole suite, so turn it off here to hit the disabled path.
    with (
        patch("nrtk._experimental.enabled", new=False),
        pytest.raises(ImportError, match="import nrtk.experimental"),
    ):
        _experimental.require(f"{FAKE_MODULE}.Probe")


@pytest.mark.core
def test_opting_in_warns_once_and_access_stays_quiet() -> None:
    # The warning belongs to the opt-in, not to each symbol: plugin discovery
    # getattrs everything __dir__ advertises, so warning on access meant every
    # get_impls() call narrated classes the caller never asked for.
    with pytest.warns(_experimental.ExperimentalWarning, match="Experimental NRTK features"):
        importlib.reload(nrtk.experimental)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _experimental.require(f"{FAKE_MODULE}.Probe")


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
