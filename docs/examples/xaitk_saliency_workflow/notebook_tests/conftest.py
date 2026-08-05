"""Pytest configuration for notebook utility tests.

Adds the utils directory to sys.path so that the ``image_classification``
and ``object_detection`` packages are importable during test collection.
"""

import sys
from pathlib import Path

# Add the utils directory to sys.path so notebook utility packages are importable
utils_path = str(Path(__file__).resolve().parent.parent / "utils")
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)
