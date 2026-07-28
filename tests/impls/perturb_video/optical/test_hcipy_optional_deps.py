"""Test import guard behavior for HCIPy optical video perturbers."""

from importlib import import_module
from unittest.mock import patch

import pytest

from tests._utils.import_guard_tests_mixin import ImportGuardTestsMixin, mock_missing_deps


class TestHcipyPerturberImportGuard(ImportGuardTestsMixin):
    """Test import guard for TurbulenceVideoPerturber when hcipy is unavailable."""

    MODULE_PATH = "nrtk.impls.perturb_video.optical"
    DEPS_TO_MOCK = ["hcipy"]
    CLASSES = [
        "TurbulenceVideoPerturber",
    ]
    ERROR_MATCH = (
        r"{class_name} requires the `hcipy` extra\. "
        r"Install with: `pip install nrtk\[hcipy\]`"
    )


@pytest.mark.core
def test_experimental_guard_precedes_hcipy_guard() -> None:
    """The experimental error takes precedence when both gates are closed."""
    module_path = "nrtk.impls.perturb_video.optical"
    with mock_missing_deps(module_path=module_path, deps_to_mock=["hcipy"]):
        module = import_module(module_path)
        with (
            patch("nrtk._experimental.enabled", new=False),
            pytest.raises(ImportError, match="import nrtk.experimental"),
        ):
            _ = module.TurbulenceVideoPerturber

        # Enabling experimental features after importing the package must
        # advance to the optional-extra guard rather than using stale state
        with pytest.raises(ImportError, match=r"requires the `hcipy` extra"):
            _ = module.TurbulenceVideoPerturber


@pytest.mark.hcipy
@pytest.mark.usefixtures("require_marker")
def test_enable_experimental_after_module_import() -> None:
    """A package imported while disabled loads normally after later opt-in."""
    module_path = "nrtk.impls.perturb_video.optical"
    with mock_missing_deps(module_path=module_path, deps_to_mock=[]):
        with patch("nrtk._experimental.enabled", new=False):
            module = import_module(module_path)
        assert module.TurbulenceVideoPerturber.__module__ == module_path


@pytest.mark.hcipy
@pytest.mark.usefixtures("require_marker")
def test_scipy_import_guard() -> None:
    """Missing scipy triggers the TurbulenceVideoPerturber import guard.

    scipy is installed via the `hcipy` extra and imported by the perturber.
    This must run where hcipy is importable: the module imports hcipy before
    scipy, so in a no-hcipy environment the import would fail on hcipy first and
    prove nothing about scipy. ``importorskip`` enforces that, and the ``hcipy``
    marker selects this in hcipy-capable CI jobs. Written as a standalone test
    (not an ImportGuardTestsMixin subclass) because the mixin hard-codes the
    ``core`` marker, which would (mis)run this in no-hcipy environments.
    """
    pytest.importorskip("hcipy")

    module_path = "nrtk.impls.perturb_video.optical"
    with mock_missing_deps(module_path=module_path, deps_to_mock=["scipy"]):
        module = import_module(module_path)
        assert "TurbulenceVideoPerturber" not in module.__all__
        with pytest.raises(
            ImportError,
            match=(
                r"TurbulenceVideoPerturber requires the `hcipy` extra\. "
                r"Install with: `pip install nrtk\[hcipy\]`"
            ),
        ):
            _ = module.TurbulenceVideoPerturber


@pytest.mark.hcipy
@pytest.mark.usefixtures("require_marker")
def test_hcipy_public_imports() -> None:
    """Canary test: FAIL if hcipy marker is used but perturbers can't be imported.

    When running `pytest -m hcipy`, this test asserts that the environment was
    built with the hcipy extra. If hcipy is not installed, this test
    FAILS (not skips) to indicate a CI/environment configuration error.
    """
    try:
        from nrtk.impls.perturb_video.optical import TurbulenceVideoPerturber

        del TurbulenceVideoPerturber
    except ImportError as e:
        pytest.fail(
            f"Running with hcipy marker but perturbers not importable: {e}. Ensure hcipy extra is installed.",
        )
