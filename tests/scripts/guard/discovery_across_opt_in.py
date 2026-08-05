"""Plugin discovery must find experimental implementations, and only after opting in.

This is the script behind the requirement that ``get_impls()`` not return an empty
set and not depend on what has already been imported. Before this change the
experimental gate was read at first import rather than at lookup, so a gated
implementation's visibility depended on import order, and a module that was never
registered under ``smqtk_plugins`` could not be discovered at all.

The subject is a fixture -- ``tests/_utils/guard_plugin`` -- rather than a real NRTK
implementation. What is under test is the guard's machinery, so it should not be
coupled to whatever NRTK currently ships: the only real implementation that fits
(experimental, and importable with no extras) is temporary, and once it graduates
there may be none left. The fixture is registered for discovery by a synthetic
distribution written below, so nothing about this reaches the published package.

Prints five labelled booleans, all expected ``True``, in the order the steps run::

    inert=  hidden_before=  found=  via_entrypoint=  visible_after=

``inert``
    Gate closed, walking every registered entrypoint wakes no gated implementation.
    Registering an experimental module must cost ordinary users nothing. Runs first,
    while nothing has opted in.
``hidden_before``
    A gated package imported *before* ``nrtk.experimental`` advertises nothing.
``found``
    Once opted in, discovery returns the implementation -- the "not an empty set" half.
``via_entrypoint``
    Its leaf module was absent from ``sys.modules`` beforehand, so discovery reached
    it through the entrypoint rather than through the import in ``hidden_before``.
    Only meaningful while the leaf is unimported, hence before ``visible_after``.
``visible_after``
    The package imported back in ``hidden_before`` advertises the name now -- the
    "not influenced by import order" half, and what reading the gate at lookup buys.

One script rather than five because each step depends on the state the previous one
left behind. A fresh interpreter because ``tests/conftest.py`` opts in for the whole
suite, so in-process there is no closed gate left to observe.
"""

import pathlib
import sys
import tempfile
import warnings

PLUGIN = "tests._utils.guard_plugin"
LEAF = f"{PLUGIN}._impl"
SYMBOL = "GuardedThingImpl"


def _register(directory: pathlib.Path) -> None:
    """Write a distribution that registers the fixture under ``smqtk_plugins``.

    Synthesised rather than declared in ``pyproject.toml`` so a test fixture never
    ships, and rather than patching smqtk's entrypoint lookup so that the real
    lookup is what gets exercised -- being registered at all was half the original
    bug.
    """
    dist_info = directory / "guard_plugin_fixture-0.0.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: guard-plugin-fixture\nVersion: 0.0.0\n",
    )
    (dist_info / "entry_points.txt").write_text(f"[smqtk_plugins]\nguard_plugin = {PLUGIN}\n")
    sys.path.insert(0, str(directory))


def main() -> None:
    """Run the sequence and print what each step observed."""
    warnings.simplefilter("ignore")
    sys.path.insert(0, str(pathlib.Path.cwd()))  # the fixture lives under tests/

    with tempfile.TemporaryDirectory() as directory:
        _register(pathlib.Path(directory))

        from tests._utils.guard_plugin._interface import GuardedThing

        # Walks every registered entrypoint, gate still closed. Inert means the walk
        # neither discovered the gated implementation nor imported its leaf on the way.
        discovered_before = {impl.__name__ for impl in GuardedThing.get_impls()}
        inert = SYMBOL not in discovered_before and LEAF not in sys.modules

        import tests._utils.guard_plugin as plugin

        hidden_before = SYMBOL not in dir(plugin)

        import nrtk.experimental  # noqa: F401 - opting in is the whole point

        # Sampled before discovery runs, so the flag below cannot be confused by an
        # import this script did itself. Also keeps a statement between the opt-in and
        # the call that depends on it, where an import sorter could otherwise swap them.
        leaf_was_imported = LEAF in sys.modules

        found = SYMBOL in {impl.__name__ for impl in GuardedThing.get_impls()}
        via_entrypoint = not leaf_was_imported and LEAF in sys.modules

        visible_after = SYMBOL in dir(plugin)

    print(
        f"inert={inert} hidden_before={hidden_before} found={found} "
        f"via_entrypoint={via_entrypoint} visible_after={visible_after}",
    )


if __name__ == "__main__":
    main()
