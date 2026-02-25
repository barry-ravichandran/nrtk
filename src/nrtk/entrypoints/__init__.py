"""Command-line interface tools."""

_MAITE_CLASSES = ["nrtk_perturber"]
_MAITE_TOOLS_CLASSES = ["nrtk_perturber_cli"]

__all__: list[str] = []

_maite_import_error: ImportError | None = None
_tools_import_error: ImportError | None = None

try:
    from nrtk.entrypoints._nrtk_perturber import nrtk_perturber as nrtk_perturber

    __all__ += _MAITE_CLASSES
except ImportError as _ex:
    _maite_import_error = _ex

try:
    from nrtk.entrypoints._nrtk_perturber_cli import nrtk_perturber_cli as nrtk_perturber_cli

    __all__ += _MAITE_TOOLS_CLASSES
except ImportError as _ex:
    _tools_import_error = _ex


def __getattr__(name: str) -> None:
    if name in _MAITE_CLASSES:
        msg = f"{name} requires the `maite` extra. Install with: `pip install nrtk[maite]`"
        if _maite_import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_maite_import_error).__name__}: {_maite_import_error}"
            )
        raise ImportError(msg)
    if name in _MAITE_TOOLS_CLASSES:
        msg = f"{name} requires the `maite` and `tools` extras. Install with: `pip install nrtk[maite,tools]`"
        if _tools_import_error is not None:
            msg += (
                f"\n\nIf the extra is already installed, the following upstream error may be the cause:"
                f"\n  {type(_tools_import_error).__name__}: {_tools_import_error}"
            )
        raise ImportError(msg)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
