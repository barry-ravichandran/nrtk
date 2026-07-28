"""Pytest configuration for HCIPy video perturber tests.

Skips this directory if hcipy extra is not installed.
"""


def pytest_ignore_collect() -> bool | None:
    """Skip this directory if HCIPy perturbers are not importable."""
    try:
        from nrtk.impls.perturb_video.optical import TurbulenceVideoPerturber

        del TurbulenceVideoPerturber
    except ImportError:
        return True
    return None
