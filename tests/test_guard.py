"""Tests for the shared import guard (``nrtk._guard``)."""

from __future__ import annotations

import ast
import json
import pathlib
from typing import Any
from unittest.mock import patch

import pytest

from nrtk._guard import Extras, Group, extra_error, guard

LEAVES = "tests._utils.guard_leaves"
FAKE_MODULE = "nrtk.fake_module"


def build(
    *,
    groups: list[Group] | None = None,
    submodules: list[str] | None = None,
    module: str = FAKE_MODULE,
) -> tuple[Any, Any, list[str], dict]:
    """Install a guard over a throwaway namespace and hand back its hooks."""
    namespace: dict[str, Any] = {"__name__": module}
    module_getattr, module_dir, module_all = guard(
        namespace=namespace,
        groups=groups or [],
        submodules=submodules or [],
    )
    return module_getattr, module_dir, module_all, namespace


ALPHA = Group(symbols={"Alpha": f"{LEAVES}.importable"})
MISSING = Group(symbols={"Gamma": f"{LEAVES}.missing"}, extras=["pybsm"])


# --------------------------------------------------------------------------- messages


@pytest.mark.core
@pytest.mark.parametrize(
    ("extras", "expected"),
    [
        (
            ["pybsm"],
            "X requires the `pybsm` extra. Install with: `pip install nrtk[pybsm]`",
        ),
        (
            ["albumentations", ("graphics", "headless")],
            "X requires the `albumentations` and (`graphics` or `headless`) extras. "
            "Install with: `pip install nrtk[albumentations,graphics]` or "
            "`pip install nrtk[albumentations,headless]`",
        ),
    ],
    ids=["single", "and-of-or"],
)
def test_extra_error_message(extras: Extras, expected: str) -> None:
    """The simplest and the hairiest requirement shapes render the promised wording.

    Between them these two cover every branch: a bare term, several terms joined
    with "and", an OR-term, singular vs plural, and one install command per way of
    satisfying the choice.
    """
    assert str(extra_error(name="X", extras=extras, cause=None)) == expected


@pytest.mark.core
def test_extra_error_appends_upstream_cause() -> None:
    """An extra that is installed but broken is the common case, so surface its error."""
    message = str(extra_error(name="X", extras=["pybsm"], cause=ImportError("boom")))
    assert "If the extra is already installed" in message
    assert "ImportError: boom" in message


# --------------------------------------------------------------------------- stable


@pytest.mark.core
def test_stable_symbols_bind_eagerly_and_are_rehomed() -> None:
    """Extras cannot change mid-process, so stable symbols resolve at guard time."""
    _, module_dir, module_all, namespace = build(groups=[ALPHA])

    assert module_all == ["Alpha"]
    assert module_dir() == ["Alpha"]
    assert namespace["Alpha"].__module__ == FAKE_MODULE  # public path, not the private leaf


@pytest.mark.core
def test_missing_extra_stays_out_of_all_and_raises_on_access() -> None:
    """A name whose extra is absent must be invisible, then explain itself when asked for."""
    module_getattr, module_dir, module_all, _ = build(groups=[ALPHA, MISSING])

    assert module_all == ["Alpha"]
    assert "Gamma" not in module_dir()
    with pytest.raises(ImportError, match=r"Gamma requires the `pybsm` extra"):
        module_getattr("Gamma")


@pytest.mark.core
def test_core_import_failure_is_not_disguised_as_a_missing_extra() -> None:
    """Nothing is optional about a group with no extras, so a failure there is a bug."""
    with pytest.raises(ImportError, match=r"not_a_real_dependency"):
        build(groups=[Group(symbols={"Gamma": f"{LEAVES}.missing"})])


@pytest.mark.core
def test_unknown_name_raises_attribute_error() -> None:
    """A typo must look like an ordinary missing attribute, not an NRTK-flavoured error."""
    module_getattr, _, _, _ = build(groups=[ALPHA])

    with pytest.raises(AttributeError, match=r"has no attribute 'NotAThing'"):
        module_getattr("NotAThing")


# --------------------------------------------------------------------------- submodules


@pytest.mark.core
def test_submodules_are_advertised_and_imported_on_demand() -> None:
    """Submodules are named up front but only imported when something reaches for one."""
    module_getattr, module_dir, module_all, namespace = build(submodules=["sub"], module=LEAVES)

    assert module_all == ["sub"]
    assert module_dir() == ["sub"]
    assert "sub" not in namespace  # not imported yet
    assert module_getattr("sub").MARKER == "sub"
    assert "sub" in namespace  # and cached once it is


# --------------------------------------------------------------------------- experimental


EXPERIMENTAL = Group(symbols={"Beta": f"{LEAVES}.importable"}, experimental=True)
EXPERIMENTAL_MISSING = Group(symbols={"Gamma": f"{LEAVES}.missing"}, extras=["hcipy"], experimental=True)


@pytest.mark.core
def test_experimental_is_hidden_and_refused_until_opted_in() -> None:
    """A closed gate advertises nothing, which is what keeps its entrypoint inert."""
    module_getattr, module_dir, module_all, _ = build(groups=[ALPHA, EXPERIMENTAL])

    with patch("nrtk._experimental.enabled", new=False):
        assert module_dir() == ["Alpha"]
        with pytest.raises(ImportError, match=r"import nrtk.experimental"):
            module_getattr("Beta")

    assert "Beta" not in module_all  # experimental never joins the public __all__


@pytest.mark.core
def test_opting_in_after_import_still_advertises() -> None:
    """The gate is read at call time, so import order cannot decide what is visible.

    This is the whole reason experimental resolves lazily: a module imported
    before ``nrtk.experimental`` must still expose its experimental names after.
    """
    module_getattr, module_dir, _, _ = build(groups=[EXPERIMENTAL])

    with patch("nrtk._experimental.enabled", new=False):
        before = module_dir()

    assert before == []
    assert module_dir() == ["Beta"]
    assert module_getattr("Beta").__module__ == FAKE_MODULE


@pytest.mark.core
def test_experimental_gate_is_checked_before_the_extras_gate() -> None:
    """Telling someone to install an extra for a class they cannot reach yet is unhelpful."""
    module_getattr, _, _, _ = build(groups=[EXPERIMENTAL_MISSING])

    with (
        patch("nrtk._experimental.enabled", new=False),
        pytest.raises(ImportError, match=r"import nrtk.experimental"),
    ):
        module_getattr("Gamma")

    with pytest.raises(ImportError, match=r"Gamma requires the `hcipy` extra"):
        module_getattr("Gamma")


@pytest.mark.core
def test_dir_never_advertises_a_name_that_getattr_would_reject() -> None:
    """Plugin discovery getattrs everything ``dir()`` returns, without a guard of its own.

    One raising name would abort the whole discovery pass, so an experimental
    symbol whose extra is missing must not be advertised even with the gate open.
    """
    module_getattr, module_dir, _, _ = build(groups=[EXPERIMENTAL, EXPERIMENTAL_MISSING])

    assert module_dir() == ["Beta"]
    for name in module_dir():
        module_getattr(name)  # must not raise


# --------------------------------------------------------------------- real modules
#
# The cases above run against throwaway leaves. These two run against the real
# package, in-process: ``tests/conftest.py`` opts in to experimental features for
# the whole suite, and ``__all__`` is fixed at guard time, so neither needs a
# fresh interpreter the way ``tests/test_import_guards_e2e.py`` does.


@pytest.mark.core
def test_experimental_names_stay_out_of_the_public_all() -> None:
    """``__all__`` drives ``from nrtk.x import *``, so a gated name there would leak.

    Checked on the real packages rather than a fake namespace because the risk is
    a module declaring an experimental group and then advertising it anyway.
    Every module that declares an ``experimental=True`` group belongs here.
    """
    import nrtk.impls.perturb_video
    import nrtk.impls.perturb_video.optical
    import nrtk.interfaces
    import nrtk.interop

    assert "FramewisePerturber" not in nrtk.impls.perturb_video.__all__
    assert "TurbulenceVideoPerturber" not in nrtk.impls.perturb_video.optical.__all__
    assert "MAITEMultiobjectTrackingAugmentation" not in nrtk.interop.__all__
    assert "PerturbVideo" not in nrtk.interfaces.__all__
    assert "VideoFrame" not in nrtk.interfaces.__all__


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


@pytest.mark.core
def test_discovery_never_returns_a_private_implementation() -> None:
    """``__subclasses__`` recursion sees every class, so private ones must be filtered.

    smqtk discovers via ``__subclasses__()`` as well as entrypoints, and that path
    consults no name, ``__all__``, ``__dir__``, or entrypoint. A private base class or
    helper therefore reaches ``get_impls()`` the moment anything imports it, which the
    import guard cannot prevent. ``nrtk.interfaces._plugfigurable`` filters it instead.
    """
    from nrtk.interfaces import PerturbImage, PerturbImageFactory, PerturbVideo

    leaked = [
        f"{impl.__module__}.{impl.__name__}"
        for interface in (PerturbImage, PerturbImageFactory, PerturbVideo)
        for impl in interface.get_impls()
        if _is_private_nrtk_path(path=f"{impl.__module__}.{impl.__name__}")
    ]

    assert not leaked, "\n".join(leaked)


@pytest.mark.core
def test_config_round_trip_records_the_public_path() -> None:
    """Re-homing is what keeps a serialized config on the stable name.

    Without it the config would record the private leaf module, which is not a
    path anyone should be pinning, and which discovery cannot resolve back.

    Checked recursively: a nested default is just as capable of pinning a private
    path as the outer type, and only the outer one used to be asserted on.
    """
    from smqtk_core.configuration import from_config_dict, to_config_dict

    from nrtk.impls.perturb_video import FramewisePerturber
    from nrtk.interfaces import PerturbVideo

    config = json.loads(json.dumps(to_config_dict(FramewisePerturber())))
    assert "nrtk.impls.perturb_video.FramewisePerturber" in config, config
    assert not _private_type_paths(config), config

    rebuilt = from_config_dict(config=config, type_iter=PerturbVideo.get_impls())
    assert type(rebuilt).__name__ == "FramewisePerturber"


# --------------------------------------------------------------- no self-imports


def _is_submodule(*, src: pathlib.Path, package: str, name: str) -> bool:
    """Whether ``package.name`` is a module on disk rather than a guard-bound name."""
    dotted = f"{package}.{name}"
    candidate = src.parent / dotted.replace(".", "/")
    return candidate.with_suffix(".py").exists() or candidate.is_dir()


def _self_imports(*, src: pathlib.Path, path: pathlib.Path) -> list[str]:
    """Report every bound name *path* imports from the package that contains it."""
    relative = str(path.relative_to(src)).removesuffix(".py")
    dotted = "nrtk." + relative.replace("/", ".")
    package = dotted.rsplit(".", maxsplit=1)[0]
    offenders = []
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module == package:
            offenders += [
                f"{path.relative_to(src.parent)}:{node.lineno} imports {alias.name!r} from "
                f"{package!r}; import it from its leaf module instead"
                for alias in node.names
                if not _is_submodule(src=src, package=package, name=alias.name)
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
    src = pathlib.Path(__file__).resolve().parent.parent / "src" / "nrtk"
    offenders: list[str] = []
    for path in sorted(src.rglob("*.py")):
        if path.name != "__init__.py":
            offenders += _self_imports(src=src, path=path)

    assert not offenders, "\n".join(offenders)


# ----------------------------------------------------------- TYPE_CHECKING blocks


def _guard_call(tree: ast.Module) -> ast.Call | None:
    """The module-level ``guard(...)`` call, or None if this module does not install one."""
    return next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "guard"
        ),
        None,
    )


def _keyword(*, call: ast.Call, name: str) -> ast.expr | None:
    """The value passed to keyword *name*, or None if it was not passed."""
    return next((keyword.value for keyword in call.keywords if keyword.arg == name), None)


def _string_list(node: ast.expr | None) -> set[str]:
    """The string literals in a list literal, ignoring anything else."""
    elements = getattr(node, "elts", [])
    return {e.value for e in elements if isinstance(e, ast.Constant) and isinstance(e.value, str)}


def _symbol_mappings(groups_arg: ast.expr | None) -> list[ast.expr | None]:
    """The ``symbols=`` argument of every ``Group(...)`` in a ``groups=[...]`` list."""
    groups = getattr(groups_arg, "elts", [])
    return [_keyword(call=group, name="symbols") for group in groups if isinstance(group, ast.Call)]


def _symbols(groups_arg: ast.expr | None) -> tuple[set[str], list[str]]:
    """The declared symbol names, plus complaints about anything unreadable statically.

    A ``symbols`` key built at runtime would make the whole check silently
    under-report, so it is called out rather than skipped.
    """
    symbols: set[str] = set()
    unreadable: list[str] = []
    for mapping in _symbol_mappings(groups_arg):
        if not isinstance(mapping, ast.Dict):
            unreadable.append("a Group's symbols= is not a dict literal")
            continue
        keys = {k.value for k in mapping.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if len(keys) != len(mapping.keys):
            unreadable.append(f"line {mapping.lineno}: a symbols key is not a string literal")
        symbols |= keys
    return symbols, unreadable


def _type_checking_names(tree: ast.Module) -> set[str]:
    """Names bound by ``if TYPE_CHECKING:`` blocks."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.If) and getattr(node.test, "id", None) == "TYPE_CHECKING"):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.ImportFrom):
                names.update(alias.asname or alias.name for alias in child.names)
    return names


def _declaration_problems(*, src: pathlib.Path, path: pathlib.Path) -> list[str]:
    """Report where *path*'s ``if TYPE_CHECKING:`` block and its guard declaration disagree."""
    tree = ast.parse(path.read_text())
    call = _guard_call(tree)
    if call is None:
        return []

    symbols, unreadable = _symbols(_keyword(call=call, name="groups"))
    # Submodules are imported normally, so they may appear in the block without
    # being guard-bound symbols.
    annotated = _type_checking_names(tree) - _string_list(_keyword(call=call, name="submodules"))
    relative = path.relative_to(src.parent)

    problems = [f"{relative}: {complaint}" for complaint in unreadable]
    if missing := sorted(symbols - annotated):
        problems.append(f"{relative}: declared in symbols= but missing from `if TYPE_CHECKING:`: {missing}")
    if leftover := sorted(annotated - symbols):
        problems.append(f"{relative}: in `if TYPE_CHECKING:` but not declared in symbols=: {leftover}")
    return problems


@pytest.mark.core
def test_every_guarded_symbol_has_a_type_checking_import() -> None:
    """Every name in a ``symbols`` mapping needs a matching ``if TYPE_CHECKING:`` import.

    Nothing else in the repo catches this, which is the only reason the check is
    worth its length. ``__getattr__: Callable[[str], Any]`` tells pyright that every
    attribute of a guarded module exists and is ``Any``, so a symbol missing from the
    block still imports, still type-checks, and still passes
    ``pyright --verifytypes`` -- the symbol simply drops out of the exported API and
    the completeness score stays at 100% because the denominator shrinks with it.

    What is lost is silent and only visible to callers: the name resolves as ``Any``
    instead of its signature, so argument names and types stop being checked at every
    call site, the return type stops propagating, and editors lose hover, signature
    help and go-to-definition for it.

    The reverse direction matters too -- a leftover in the block is a symbol that was
    renamed or dropped from the declaration.

    Read from the source rather than from a live registry, so the check needs nothing
    added to ``nrtk`` for its own benefit and cannot be fooled by import order.
    ``_guard.py`` needs no special case: it defines ``guard`` rather than calling it,
    and the call in its docstring is a string to the parser.
    """
    src = pathlib.Path(__file__).resolve().parent.parent / "src" / "nrtk"
    problems: list[str] = []
    for path in sorted(src.rglob("*.py")):
        problems += _declaration_problems(src=src, path=path)

    assert not problems, "\n".join(problems)
