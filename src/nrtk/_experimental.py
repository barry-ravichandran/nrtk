"""Runtime state for NRTK's experimental features.

A tiny flag module that imports nothing from nrtk, so anything can read
``enabled`` without risking an import cycle. Importing :mod:`nrtk.experimental`
flips it on.
"""


class ExperimentalWarning(UserWarning):
    """Emitted once when experimental features are enabled."""


enabled: bool = False


def require(name: str) -> None:
    """Raise unless experimental features are enabled.

    The warning that goes with opting in is emitted once by
    :mod:`nrtk.experimental`, not here. Warning per symbol on access meant every
    ``get_impls()`` call narrated the experimental classes it walked past, because
    plugin discovery getattrs every name ``__dir__`` advertises.

    Args:
        name: Fully qualified symbol name, used in the message.

    Raises:
        ImportError: If experimental features are not enabled.
    """
    if not enabled:
        raise ImportError(
            f"{name} is experimental. Enable it with `import nrtk.experimental` before importing it. "
            "Experimental APIs may change without a deprecation warning.",
        )


# Exposing an experimental symbol is not done by hand. Add it to a
# ``Group(..., experimental=True)`` in the owning module's :func:`nrtk._guard.guard`
# call; see docs/development/import_guards.rst.
