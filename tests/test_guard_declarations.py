"""Checks over what every module *declares* to :func:`nrtk._guard.guard`.

``tests/test_guard.py`` owns the guard's mechanics. This module owns the other
half: that each module declares the right thing, and that whatever it declared
actually holds in the environment the tests are running in.

That second part is why there is no dependency mocking here. A guarded symbol is
either importable in this environment or it is not, and the guard has to behave
correctly either way. Asserting that invariant means the ``core`` environment
exercises every "extra is missing" path and the ``optional`` environment
exercises every "extra is present" path, over every guarded module, without
evicting anything from ``sys.modules``. The single-extra environments run only
the canaries, so a partially-satisfied multi-extra group (maite installed, tools
absent) is exercised at the code-path level here, never as a live environment
state.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import re
from collections import defaultdict
from typing import TYPE_CHECKING, cast
from unittest.mock import patch

import pytest
import yaml

if TYPE_CHECKING:
    from types import ModuleType

    from nrtk._guard import Extras, Group, _Guard

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "nrtk"
EXTRAS_YML = SRC / "utils" / "_extras.yml"
PYPROJECT = SRC.parent.parent / "pyproject.toml"


def _calls_guard(path: pathlib.Path) -> bool:
    """Whether *path* installs a guard, i.e. calls ``guard(...)`` at module level."""
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "guard"
        for node in ast.walk(ast.parse(path.read_text()))
    )


def _guarded_modules() -> list[str]:
    """Every module that installs a guard, by dotted name.

    Discovery is by ``guard()`` call rather than by package, because five of the
    call sites are plain modules (``blur.py``, ``otf.py`` and friends) rather than
    ``__init__.py`` files.
    """
    names = []
    for path in sorted(SRC.rglob("*.py")):
        if not _calls_guard(path):
            continue
        relative = path.parent if path.name == "__init__.py" else path.with_suffix("")
        names.append(".".join(("nrtk", *relative.relative_to(SRC).parts)))
    return names


def _guard_of(module: str) -> _Guard:
    """The guard *module* installed, reached through the hook it published.

    ``guard()`` hands back ``_Guard.getattr`` as a bound method and the module binds
    it as ``__getattr__``, so the instance is reachable from the module itself. That
    is deliberately the only route: a registry inside ``nrtk._guard`` would be state
    the package carries purely for these tests, and would need clearing every time a
    test installed a guard over a throwaway namespace.

    Importing is always safe here -- a guarded module has to import with no extras
    installed. ``test_import_guards_e2e.py`` pins that for every package; the
    plain-module call sites, which its walk never imports, are pinned by this
    file's own run in the ``core`` environment.
    """
    imported = importlib.import_module(module)
    hook = imported.__getattr__  # type: ignore[attr-defined]
    return cast("_Guard", hook.__self__)


GUARDED = _guarded_modules()
DECLARED = [(module, group) for module in GUARDED for group in _guard_of(module)._groups]


@pytest.mark.core
def test_every_module_installing_the_hook_is_in_the_guarded_set() -> None:
    """``GUARDED`` must not silently shrink.

    Discovery matches the literal call ``guard(...)``, so a future call through an
    alias or a wrapper would quietly drop its module from every test in this file.
    The ``__getattr__`` assignment anchors the derivation independently: binding
    the hook is required for a guard to function however the call is spelled.
    """
    hooked = []
    for path in sorted(SRC.rglob("*.py")):
        targets = {
            name.id
            for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.Assign)
            for target in node.targets
            for name in (target.elts if isinstance(target, ast.Tuple) else [target])
            if isinstance(name, ast.Name)
        }
        if "__getattr__" in targets:
            relative = path.parent if path.name == "__init__.py" else path.with_suffix("")
            hooked.append(".".join(("nrtk", *relative.relative_to(SRC).parts)))

    assert hooked == GUARDED


def _terms(extras: Extras) -> set[str]:
    """Flatten a requirement into the set of extra names it mentions."""
    names: set[str] = set()
    for term in extras:
        names.update({term} if isinstance(term, str) else set(term))
    return names


def _type_checking_names(module: str) -> set[str]:
    """Names bound by the ``if TYPE_CHECKING:`` block of *module*, ignoring submodules."""
    path = SRC.parent / pathlib.Path(*module.split("."))
    source = (path / "__init__.py") if path.is_dir() else path.with_suffix(".py")
    names: set[str] = set()
    for node in ast.walk(ast.parse(source.read_text())):
        if not (isinstance(node, ast.If) and getattr(node.test, "id", None) == "TYPE_CHECKING"):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.ImportFrom):
                names.update(alias.asname or alias.name for alias in child.names)
    return names


def _registered_for_discovery() -> set[str]:
    """Modules listed under ``smqtk_plugins`` in :file:`pyproject.toml`.

    Read from the file rather than from installed metadata, because the question is
    whether a module was ever declared, not whether this environment happens to have
    been reinstalled since.
    """
    block = re.search(
        r'\[project\.entry-points\."smqtk_plugins"\](.*?)(?:\n\[|\Z)',
        PYPROJECT.read_text(),
        re.DOTALL,
    )
    assert block, "pyproject.toml has no smqtk_plugins entry-point table"
    return set(re.findall(r'=\s*"([^"]+)"', block.group(1)))


@pytest.mark.core
def test_every_module_publishing_implementations_is_registered() -> None:
    """Being importable is not being discoverable.

    Half of the bug this guard work fixed was ``nrtk.impls.perturb_video`` never being
    registered: the guard was correct, the module imported cleanly, and
    ``get_impls()`` still came back empty because discovery had no entry to walk.

    Scoped to ``nrtk.impls`` because that is where implementations live --
    ``nrtk.interfaces`` publishes the interfaces themselves and ``nrtk.interop``
    publishes adapters, neither of which is discovered as a plugin. The check is one
    directional: a module may be registered without installing a guard.
    """
    registered = _registered_for_discovery()
    unregistered = sorted(
        module
        for module in GUARDED
        if module == "nrtk.impls" or module.startswith("nrtk.impls.")
        if any(group.symbols for group in _guard_of(module)._groups)
        if module not in registered
    )

    assert not unregistered, "declare implementations but have no smqtk_plugins entry:\n" + "\n".join(unregistered)


@pytest.mark.core
def test_every_declared_extra_exists() -> None:
    """A typo in ``extras=`` would otherwise surface only as advice nobody can follow."""
    known = set(yaml.safe_load(EXTRAS_YML.read_text()))
    unknown = sorted(
        f"{module}: {name!r}" for module, group in DECLARED for name in sorted(_terms(group.extras) - known)
    )
    assert not unknown, "extras named in a Group but absent from pyproject:\n" + "\n".join(unknown)


@pytest.mark.core
def test_no_symbol_is_claimed_by_two_groups() -> None:
    """Binding re-homes a class globally, so two groups claiming one name is a bug.

    The owner index would silently let the last group win, which means the symbol
    could resolve under a requirement it does not actually have, and ``__all__``
    would list it twice.
    """
    duplicates = []
    for module in GUARDED:
        seen: set[str] = set()
        for group in _guard_of(module)._groups:
            duplicates += [f"{module}.{name}" for name in group.symbols if name in seen]
            seen.update(group.symbols)
    assert not duplicates, f"symbols declared in more than one group: {duplicates}"


@pytest.mark.core
def test_no_leaf_symbol_is_published_by_two_modules() -> None:
    """Two modules cannot publish the same class, because re-homing is global.

    ``_bind`` sets ``__module__`` on the class object itself, so whichever module
    binds last wins and the other silently starts recording a path that does not
    resolve back to it. Different classes that merely share a *name* are fine --
    the collision is on the (leaf module, symbol) pair, which is one class.
    """
    owners: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for module in GUARDED:
        for group in _guard_of(module)._groups:
            for name, source in group.symbols.items():
                owners[source, name].append(module)

    shared = {leaf: modules for leaf, modules in owners.items() if len(modules) > 1}
    assert not shared, "a class may be published from exactly one module, but:\n" + "\n".join(
        f"  {source}.{name} is claimed by {modules}" for (source, name), modules in sorted(shared.items())
    )


@pytest.mark.core
@pytest.mark.parametrize("module", GUARDED, ids=GUARDED)
def test_type_checking_block_matches_the_declaration(module: str) -> None:
    """Every guarded symbol needs a ``TYPE_CHECKING`` import, and vice versa.

    The guard resolves names at runtime, which pyright cannot follow, so a symbol
    missing from the block is invisible to type checkers until something uses it.
    A leftover in the block is a symbol that was renamed or dropped.
    """
    module_guard = _guard_of(module)
    declared = {name for group in module_guard._groups for name in group.symbols}
    # Submodules are imported normally, so they may appear in the block without being symbols.
    annotated = _type_checking_names(module) - set(module_guard._submodules)

    assert annotated == declared, (
        f"{module}: TYPE_CHECKING imports and guard symbols disagree.\n"
        f"  declared but not annotated: {sorted(declared - annotated)}\n"
        f"  annotated but not declared: {sorted(annotated - declared)}"
    )


@pytest.mark.core
@pytest.mark.parametrize("module", GUARDED, ids=GUARDED)
def test_declaration_holds_in_this_environment(module: str) -> None:
    """Each declared symbol either resolves, or explains the extra it needs.

    Whichever branch a given environment takes, the two must never both hold and
    never both fail: a name that is advertised has to be reachable, and a name
    that is not has to say why.
    """
    imported = importlib.import_module(module)
    module_guard = _guard_of(module)

    # The gate is opened explicitly rather than inherited from tests/conftest.py's
    # session-wide opt-in, so this file does not silently depend on suite state.
    with patch("nrtk._experimental.enabled", new=True):
        for group in module_guard._groups:
            for name in group.symbols:
                _assert_symbol_is_consistent(module=module, imported=imported, name=name, group=group)


def _assert_symbol_is_consistent(*, module: str, imported: ModuleType, name: str, group: Group) -> None:
    """Assert one symbol is either reachable and re-homed, or refused with useful advice."""
    advertised = name in dir(imported)

    if group.experimental:
        assert name not in imported.__all__, f"{module}.{name} is experimental and must stay out of __all__"
    else:
        assert advertised == (name in imported.__all__), (
            f"{module}.{name}: __dir__ and __all__ disagree about whether it is available"
        )

    if advertised:
        resolved = getattr(imported, name)
        assert getattr(resolved, "__module__", module) == module, (
            f"{module}.{name} was not re-homed; a serialized config would record its private path"
        )
        return

    # Not advertised, so asking for it must explain itself rather than raising AttributeError.
    with pytest.raises(ImportError) as excinfo:
        getattr(imported, name)
    message = str(excinfo.value)
    assert group.extras, f"{module}.{name} is unavailable but declares no extras, so its failure is a bug"
    missing = sorted(term for term in _terms(group.extras) if term not in message)
    assert not missing, f"{module}.{name}: error message does not name {missing}\n  message: {message}"


# ------------------------------------------------- what the declarations imply elsewhere
#
# The checks above read a module's declaration directly. These three check
# consequences of it that show up somewhere else: in plugin discovery, in a
# serialized config, and in how other modules import the declared names.


def _is_private_nrtk_path(*, path: str) -> bool:
    """Whether *path* is an nrtk path with a private module or symbol anywhere in it."""
    parts = path.split(".")
    return parts[0] == "nrtk" and any(part.startswith("_") for part in parts)


def _private_type_paths(config: object) -> list[str]:
    """Every ``type`` string anywhere in *config* that names a private nrtk path."""
    if isinstance(config, list):
        return [path for value in config for path in _private_type_paths(value)]
    if not isinstance(config, dict):
        return []
    recorded = config.get("type")
    here = [recorded] if isinstance(recorded, str) and _is_private_nrtk_path(path=recorded) else []
    return here + [path for value in config.values() for path in _private_type_paths(value)]


def _discoverable_interfaces() -> list[type]:
    """Every ``nrtk.interfaces`` name that plugin discovery can be asked about.

    Read from ``dir()`` rather than ``__all__``: an experimental interface is
    deliberately kept out of ``__all__``, so listing that instead would quietly skip
    exactly the interfaces most likely to be wrong.
    """
    import nrtk.interfaces
    from nrtk.interfaces._plugfigurable import Plugfigurable

    return [
        candidate
        for name in dir(nrtk.interfaces)
        if isinstance(candidate := getattr(nrtk.interfaces, name), type) and issubclass(candidate, Plugfigurable)
    ]


@pytest.mark.core
def test_discovery_never_returns_a_private_implementation() -> None:
    """``__subclasses__`` recursion sees every class, so private ones must be filtered.

    smqtk discovers via ``__subclasses__()`` as well as entrypoints, and that path
    consults no name, ``__all__``, ``__dir__``, or entrypoint. A private base class or
    helper therefore reaches ``get_impls()`` the moment anything imports it, which the
    import guard cannot prevent. ``nrtk.interfaces._plugfigurable`` filters it instead.
    """
    interfaces = _discoverable_interfaces()
    assert interfaces, "no discoverable interfaces found; the walk has stopped matching"

    leaked = [
        f"{impl.__module__}.{impl.__name__}"
        for interface in interfaces
        for impl in interface.get_impls()
        if _is_private_nrtk_path(path=f"{impl.__module__}.{impl.__name__}")
    ]

    assert not leaked, "\n".join(leaked)


@pytest.mark.core
def test_config_round_trips_record_only_public_paths() -> None:
    """Re-homing is what keeps a serialized config on the stable name.

    Without it the config would record the private leaf module, which is not a
    path anyone should be pinning, and which discovery cannot resolve back.

    Every discoverable implementation that can be built with no arguments is checked,
    rather than one hand-picked class, and the config is walked recursively -- a
    nested default is just as capable of pinning a private path as the outer type.

    The config dict is inspected as-is rather than through JSON: whether a config
    serializes is a separate question from whether it names public paths, and at
    least one implementation returns a numpy array from ``get_config()``.
    """
    from smqtk_core.configuration import from_config_dict, to_config_dict

    checked: list[str] = []
    problems: list[str] = []
    for interface in _discoverable_interfaces():
        for impl in sorted(interface.get_impls(), key=lambda c: c.__name__):
            try:
                instance = impl()
            except Exception:  # noqa: BLE001, S112 - needs arguments; nothing to serialize here
                continue
            config = to_config_dict(instance)
            checked.append(impl.__name__)
            problems += [f"{impl.__name__}: {path}" for path in _private_type_paths(config)]
            rebuilt = from_config_dict(config=config, type_iter=interface.get_impls())
            if type(rebuilt) is not impl:
                problems.append(f"{impl.__name__}: round-tripped to {type(rebuilt).__name__}")

    assert not problems, "\n".join(problems)
    assert checked, "no implementation could be constructed; the walk has stopped matching"


def _is_submodule(*, package: str, name: str) -> bool:
    """Whether ``package.name`` is a module on disk rather than a guard-bound name."""
    dotted = f"{package}.{name}"
    candidate = SRC.parent / dotted.replace(".", "/")
    return candidate.with_suffix(".py").exists() or candidate.is_dir()


def _self_imports(*, path: pathlib.Path) -> list[str]:
    """Report every bound name *path* imports from the package that contains it.

    ``from . import X`` is the same import spelled relatively, so it is matched too.
    """
    relative = str(path.relative_to(SRC)).removesuffix(".py")
    dotted = "nrtk." + relative.replace("/", ".")
    package = dotted.rsplit(".", maxsplit=1)[0]
    offenders = []
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and (node.module == package or (node.level == 1 and node.module is None)):
            offenders += [
                f"{path.relative_to(SRC.parent)}:{node.lineno} imports {alias.name!r} from "
                f"{package!r}; import it from its leaf module instead"
                for alias in node.names
                if not _is_submodule(package=package, name=alias.name)
            ]
    return offenders


@pytest.mark.core
def test_no_module_imports_a_bound_name_from_its_own_package() -> None:
    """A module must not import a guard-bound name from the package that contains it.

    ``from nrtk.interfaces import PerturbImage`` inside ``nrtk/interfaces/_x.py``
    reaches back through a package that is still executing its own ``guard()`` call,
    so it resolves only if that name happens to have been bound already. That makes
    the order of a ``symbols`` dict load-bearing: reordering it, or inserting an
    entry above the wrong line, breaks the import with a confusing circular-import
    error. Naming the leaf module directly carries no such dependency.

    Importing a *submodule* from the parent package stays fine -- the import system
    resolves those regardless of what has been bound.
    """
    offenders: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        if path.name != "__init__.py":
            offenders += _self_imports(path=path)

    assert not offenders, "\n".join(offenders)
