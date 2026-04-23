# NRTK-XAITK Workflow Examples

End-to-end workflows that combine [nrtk](https://github.com/Kitware/nrtk) with
[xaitk-saliency](https://github.com/XAITK/xaitk-saliency) for perturbation-based
saliency analysis on image classification and object detection tasks.

## Why Is This Separate from `src/nrtk`?

The utilities in this directory are **notebook-specific helpers**, not part of
the `nrtk` package. They are kept separate because:

- They wrap third-party models and datasets (Ultralytics YOLO, HuggingFace
  Transformers, VisDrone) into
  [MAITE](https://github.com/mit-ll-ai-technology/maite) protocols for use in
  the example notebooks.
- They depend on packages (`xaitk-saliency`, `torch`, `ultralytics`, `datasets`,
  `transformers`) that are **not** `nrtk` dependencies.
- They are intended for demonstration purposes only and are not installed as
  part of `pip install nrtk`.

## Directory Structure

```text
nrtk_xaitk_workflow/
├── README.md
├── image_classification_perturbation_saliency.ipynb   # IC notebook
├── object_detection_perturbation_saliency.ipynb       # OD notebook
├── utils/                                             # Notebook utility packages
│   ├── __init__.py
│   ├── image_classification/
│   │   ├── __init__.py
│   │   ├── dataset.py          # Public module (import guard + re-exports)
│   │   ├── _dataset.py         # Private module (implementation)
│   │   ├── model.py            # Public module
│   │   └── _model.py           # Private module
│   └── object_detection/
│       ├── __init__.py
│       ├── dataset.py
│       ├── _dataset.py
│       ├── model.py
│       └── _model.py
└── notebook_tests/              # Tests for the utilities
    ├── conftest.py              # sys.path setup for utils/ and project root
    ├── __init__.py
    ├── image_classification/
    │   ├── __init__.py
    │   ├── test_dataset.py
    │   └── test_model.py
    └── object_detection/
        ├── __init__.py
        ├── test_dataset.py
        └── test_model.py
```

## Utilities

Each utility package (`image_classification`, `object_detection`) follows a
**public/private module split** consistent with the pattern used in `src/nrtk`:

- **Public modules** (`dataset.py`, `model.py`) are thin re-export wrappers with
  import guards. When optional dependencies are missing, accessing a guarded
  name raises `ImportError` with an install hint.
- **Private modules** (`_dataset.py`, `_model.py`) contain the actual
  implementation and import third-party packages directly.

This ensures notebooks fail with clear instructions rather than cryptic
`ModuleNotFoundError` tracebacks.

## Tests

The `notebook_tests/` directory contains tests for the utility modules. These
tests live alongside the utilities rather than in the project's main `tests/`
directory because the utilities themselves are not part of the `nrtk` package.

Tests are organized by pytest markers:

| Marker  | Purpose                                    | Dependencies       |
| ------- | ------------------------------------------ | ------------------ |
| `core`  | Import guard behavior (mocks missing deps) | None beyond `nrtk` |
| `xaitk` | Canary tests verifying real imports work   | All notebook deps  |

### Running locally (from project root)

```bash
# Import guard tests (always pass — deps are mocked)
python -m pytest -m "core" \
  docs/examples/nrtk_xaitk_workflow/notebook_tests/ \
  -o "addopts=" -o "testpaths=" -v --tb=short

# Canary tests (require real dependencies)
python -m pytest -m "xaitk" \
  docs/examples/nrtk_xaitk_workflow/notebook_tests/ \
  -o "addopts=" -o "testpaths=" -v --tb=short
```

The `-o "addopts=" -o "testpaths="` flags override the root `pyproject.toml`
defaults, which target `src/nrtk` coverage and the `tests/` directory.
