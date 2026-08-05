"""The guard's mechanics, exercised against throwaway leaves.

Everything here builds a guard over a fake namespace and checks how it behaves:
message wording, eager versus lazy resolution, and the rule that ``__dir__``
never advertises a name ``__getattr__`` would reject. Nothing here reads the real
package, so adding an implementation never means editing this file.

What each module *declares* is checked in ``tests/test_guard_declarations.py``,
and the two claims that only hold across a whole process live in
``tests/test_import_guards_e2e.py``.
"""

from __future__ import annotations

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


# Extras here are deliberately fictional. Nothing in this file needs a real one: the
# leaf behind MISSING fails whatever is installed, and the rest is string rendering.
# That real declarations only name extras that exist is checked against pyproject in
# ``tests/test_guard_declarations.py``.
EXTRA_A = "extra-a"
EXTRA_B = "extra-b"
EXTRA_C = "extra-c"

ALPHA = Group(symbols={"Alpha": f"{LEAVES}.importable"})
MISSING = Group(symbols={"Gamma": f"{LEAVES}.missing"}, extras=[EXTRA_A])


# --------------------------------------------------------------------------- messages


@pytest.mark.core
@pytest.mark.parametrize(
    ("extras", "expected"),
    [
        (
            [EXTRA_A],
            "X requires the `extra-a` extra. Install with: `pip install nrtk[extra-a]`",
        ),
        (
            [EXTRA_A, (EXTRA_B, EXTRA_C)],
            "X requires the `extra-a` and (`extra-b` or `extra-c`) extras. "
            "Install with: `pip install nrtk[extra-a,extra-b]` or "
            "`pip install nrtk[extra-a,extra-c]`",
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
    message = str(extra_error(name="X", extras=[EXTRA_A], cause=ImportError("boom")))
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
    with pytest.raises(ImportError, match=r"Gamma requires the `extra-a` extra"):
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
EXPERIMENTAL_MISSING = Group(symbols={"Gamma": f"{LEAVES}.missing"}, extras=[EXTRA_B], experimental=True)


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

    with patch("nrtk._experimental.enabled", new=True):
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

    with (
        patch("nrtk._experimental.enabled", new=True),
        pytest.raises(ImportError, match=r"Gamma requires the `extra-b` extra"),
    ):
        module_getattr("Gamma")


@pytest.mark.core
def test_dir_never_advertises_a_name_that_getattr_would_reject() -> None:
    """Plugin discovery getattrs everything ``dir()`` returns, without a guard of its own.

    One raising name would abort the whole discovery pass, so an experimental
    symbol whose extra is missing must not be advertised even with the gate open.
    """
    module_getattr, module_dir, _, _ = build(groups=[EXPERIMENTAL, EXPERIMENTAL_MISSING])

    with patch("nrtk._experimental.enabled", new=True):
        assert module_dir() == ["Beta"]
        for name in module_dir():
            module_getattr(name)  # must not raise
