Testing Architecture
********************

NRTK uses `tox <https://tox.wiki/en/stable/>`_ to run its test suite in isolated
environments. This page explains the architecture, the reasoning behind it,
and how the pieces fit together — from import guards in the source code, to
pytest markers on test classes, to the tox environments that tie it all
together, to the GitLab CI pipeline that runs them per commit.


.. _running-tests:

Quick Start
===========

.. note::
   Tox is not included in the Poetry dependency groups. Install it separately
   before running the commands below:

   .. prompt:: bash

       pipx install tox

Common Commands
---------------

Run the core tests (no optional extras):

.. prompt:: bash

    tox -e py310-core

Run tests for a specific extra:

.. prompt:: bash

    tox -e py310-pybsm

Run all test groups for one Python version:

.. prompt:: bash

    tox -f py310

List all available environments:

.. prompt:: bash

    tox list

Run the linting, formatting and type checks:

.. prompt:: bash

    tox -e precommit

.. tip::
   Replace ``310`` with your Python version (``311``, ``312``, ``313``, or ``314``).

The hooks are declared as bare commands with ``language: system``, so they run
in whatever environment invoked ``pre-commit``. ``poetry run pre-commit run
--all-files`` and a plain ``git commit`` are equivalent ways to run the same
checks; they differ only in which environment the hooks inherit. Whichever you
use has to satisfy :file:`pyproject.toml` including its extras, because
``pyright`` reports real failures against a stale or extras-less environment.
The ``precommit`` tox environment is rebuilt from the declared constraints, so
it cannot drift; a Poetry environment needs keeping in sync:

.. prompt:: bash

    poetry sync --with main,linting,tests,docs --all-extras

The first run will be slow as tox creates a fresh virtualenv for every
environment. Subsequent runs reuse cached environments and are significantly
faster.

.. _env-extras-table:

Environment-to-Extras Mapping
-----------------------------

Each tox environment name follows the pattern ``py<version>-<factor>``,
where the factor directly corresponds to one of the project's optional extras
(e.g., ``py310-pybsm`` installs ``nrtk[pybsm]``). The special ``core``
factor installs nrtk with no extras, and ``doctests`` installs all of them.
Run ``tox list`` to see every available environment.

Adding a New Implementation
---------------------------

When adding a perturber (or any class) that depends on an optional package:

1. Add the class to a ``Group`` in the owning module's ``guard()`` call, and to
   its ``if TYPE_CHECKING:`` imports (see :doc:`import_guards`).
2. Add a pytest marker to :file:`pyproject.toml` if the dependency group is
   new (see `Pytest Markers`_).
3. Decorate test classes with ``@pytest.mark.<marker>``.
4. Add a ``conftest.py`` with ``pytest_ignore_collect()`` in the test
   directory (see `Directory-Level Collection Skipping`_).
5. Add a canary test for the new dependency group (see `Canary Tests`_).
6. Add an ``ImportGuardTestsMixin`` subclass (see `Import Guard Mixin Tests`_).
7. Wire up a new tox environment in :file:`tox.ini` if the dependency group
   is new (see `Tox Configuration`_).


Why Isolated Test Environments?
===============================

NRTK's value proposition includes a **modular dependency model**: users can
``pip install nrtk[pybsm]`` to get only the pyBSM optical perturbers, or
deploy ``nrtk`` core into a restricted environment with zero optional
dependencies. This means the codebase must work correctly with *any subset*
of its 10 optional extras installed.

To guarantee this, each test group runs in an environment that has *only* the
extras that group needs. If a test accidentally imports ``cv2`` in an
environment that only has ``pillow`` installed, it fails — catching a real
dependency leak that would affect users.


Import Guards
=============

Every module that exposes a conditional implementation declares it through
``nrtk._guard.guard()``, which installs the module's :pep:`562` hooks. That is
what makes the isolation above testable: ``import nrtk`` succeeds regardless of
which extras are installed, and a user only sees an error — naming the extra to
install — when they reach for a perturber whose dependency is missing.

:doc:`import_guards` is the reference for how to declare one. This page only
covers how the guards are *tested*; see `Import Guard Mixin Tests`_ below.


Pytest Markers
==============

Every test class (or function) is decorated with a **pytest marker** that
declares which optional dependency it requires. These markers are defined in
:file:`pyproject.toml`:

.. code-block:: toml

   # pyproject.toml (excerpt — see the file for the full list)
   [tool.pytest.ini_options]
   markers = [
       "core: Run tests that only require core functionality",
       "opencv: Run tests that require the graphics or headless extra",
       "pybsm: Run tests that require the pybsm extra",
       # ... one marker per optional extra ...
   ]

Tests apply these as class-level decorators:

.. pytestmark: skip
.. code-block:: python

   import pytest
   from tests.impls.perturb_image.perturber_tests_mixin import PerturberTestsMixin

   @pytest.mark.opencv
   class TestGaussianBlurPerturber(PerturberTestsMixin):
       ...

Each tox environment runs ``pytest -m "<marker>"`` so that only the tests
matching the installed extras are collected. Some marker expressions use
boolean logic to handle overlapping dependencies:

- ``opencv``: ``pytest -m "opencv and not albumentations"`` — runs
  OpenCV-only tests, excluding those that also require Albumentations.
- ``albumentations``: ``pytest -m "albumentations and opencv"`` — runs tests
  that need both Albumentations and OpenCV together.
- ``maite``: ``pytest -m "maite and not tools"`` — runs MAITE interop tests,
  excluding CLI/entrypoint tests that also need the ``tools`` extra.
- ``tools``: ``pytest -m "maite and tools"`` — runs only the entrypoint tests
  that require both extras.


Safety Nets
===========

Beyond markers, the test suite includes two additional safety mechanisms:

Directory-Level Collection Skipping
------------------------------------

Each test directory containing optional-dependency tests has a
``conftest.py`` that implements ``pytest_ignore_collect()``:

.. code-block:: python

   # tests/impls/perturb_image/photometric/blur/conftest.py

   def pytest_ignore_collect() -> bool | None:
       """Skip this directory if blur perturbers are not importable."""
       try:
           from nrtk.impls.perturb_image.photometric.blur import (
               AverageBlurPerturber, GaussianBlurPerturber, MedianBlurPerturber,
           )
           del AverageBlurPerturber, GaussianBlurPerturber, MedianBlurPerturber
       except ImportError:
           return True
       return None

This prevents collection errors if a marker is misapplied — the directory is
silently skipped rather than causing a test run failure.

Canary Tests
------------

Each optional-dependency group includes a **canary test** that attempts to
import the expected classes and calls ``pytest.fail()`` (not ``pytest.skip()``)
if the import fails:

.. pytestmark: opencv
.. code-block:: python

   import pytest

   @pytest.mark.opencv
   def test_opencv_public_imports() -> None:
       """Canary test: FAIL if opencv marker is used but blur perturbers can't be imported."""
       try:
           from nrtk.impls.perturb_image.photometric.blur import (
               AverageBlurPerturber, GaussianBlurPerturber, MedianBlurPerturber,
           )
           del AverageBlurPerturber, GaussianBlurPerturber, MedianBlurPerturber
       except ImportError as e:
           pytest.fail(
               f"Running with opencv marker but blur perturbers not importable: {e}. "
               f"Ensure graphics or headless extra is installed.",
           )

This catches CI configuration errors where a tox environment is supposed to
have an extra installed but doesn't, producing an explicit failure rather than
silently skipping all the tests that depend on it.

Import Guard Mixin Tests
------------------------

Import guard behavior itself is tested via the ``ImportGuardTestsMixin``
(in ``tests/_utils/import_guard_tests_mixin.py``). These tests are marked
``core`` — they run in the core environment with no extras installed. The
mixin temporarily injects ``None`` into ``sys.modules`` to simulate a missing
dependency, then verifies:

- Guarded classes raise the expected ``ImportError`` with correct
  installation instructions.
- Guarded classes are excluded from the module's ``__all__``.
- Always-available classes remain importable.
- Unknown attribute access raises ``AttributeError``.

The guard itself is covered by two further modules. ``tests/test_guard.py``
unit-tests ``nrtk._guard`` against throwaway leaf modules in
``tests/_utils/guard_leaves/`` — message wording for each requirement shape,
eager versus lazy resolution, and the rule that ``__dir__`` never advertises a
name ``__getattr__`` would reject. It also holds the two checks that need the
real packages rather than fakes but still run *in-process* — in the same
interpreter as the rest of the suite, where ``tests/conftest.py`` has already
opted in to experimental features: that no experimental name reaches ``__all__``,
and that a serialized config records the public path.

``tests/test_import_guards_e2e.py`` is reserved for the claims that cannot hold
in-process, because they only mean anything in an interpreter that has not
already imported half of nrtk. Each is checked by running a *program* — an
ordinary module under ``tests/_utils/guard_programs/``, run as a subprocess,
which prints a single line the test asserts on. There are only two, one per
program:

``packages_import_without_extras``
    The compliance walk. Every package under ``nrtk`` imports with all optional
    dependencies blocked by a meta-path finder, so the check is real even in the
    all-extras environment.

``discovery_across_opt_in``
    Confirms ``get_impls()`` neither comes back empty nor depends on import order. Walking
    the experimental gate from closed to open in one interpreter: entrypoints stay
    inert while it is shut, a package imported first advertises nothing, discovery
    reaches the implementation through its entrypoint once opted in, and the
    already-imported package advertises it afterwards. Those five observations are
    one program because each depends on the state the previous one left behind, and
    none survive an interpreter where ``tests/conftest.py`` has already opted in.

The two programs under ``tests/_utils/guard_programs/`` are real ``.py`` files
rather than source passed to ``python -c``, so that ruff and pyright check them,
and so that a failure points at a real line. Reach for one only when import order or a
process-global gate is the thing under test; anything else belongs in
``tests/test_guard.py``.


Tox Configuration
=================

The :file:`tox.ini` at the repository root defines the full test matrix.

Default Environments
--------------------

The default matrix is:

.. code-block:: ini

   py{310,311,312,313,314}-{core,opencv,albumentations,pillow,waterdroplet,skimage,diffusion,pybsm,hcipy,maite,tools,optional,doctests}

Each environment:

1. Creates an isolated virtualenv (``skip_install = true``, dependencies
   installed explicitly via ``deps``).
2. Installs ``nrtk`` in editable mode with only the extras for that factor.
3. Installs the ``tests`` dependency group (pytest, pytest-cov, pytest-xdist,
   syrupy, etc.).
4. Sets ``CUDA_VISIBLE_DEVICES`` to empty (prevents GPU contention).
5. Writes coverage to a per-environment file (``.coverage.<envname>``).
6. Runs ``pytest -m "<marker>" -n auto`` with JUnit XML output.

See the :ref:`Environment-to-Extras Mapping <env-extras-table>` section for
more on how factors map to extras.

Standalone Environments
-----------------------

These are **not** included in the default ``tox`` run or factor-filtered
runs (``tox -f py310``). They must be invoked explicitly because they serve
specialized purposes.

``py{310,...}-notebooks``
   Runs ``pyright`` type checking over the example notebooks. This
   environment has its own heavily-pinned dependency set (torch, ultralytics,
   numpy, etc.) that is intentionally kept in :file:`tox.ini` rather than
   :file:`pyproject.toml` to avoid dependency resolution conflicts with the
   rest of the project.

``coverage``
   Combines per-environment ``.coverage.*`` artifact files into a single
   report, generates a Cobertura XML file, and enforces a 90% line-coverage
   threshold (a JATIC SDP requirement). Run ``tox -f py310`` first, then
   ``tox -e coverage``.

``papermill``
   Executes Jupyter notebooks end-to-end using
   `papermill <https://papermill.readthedocs.io/en/stable/>`_. This environment builds
   a local wheel of ``nrtk`` and installs it (simulating a PyPI install) so
   notebooks exercise the same code path users would see.

``precommit``
   Runs every hook in :file:`.pre-commit-config.yaml` over all files:
   `ruff <https://docs.astral.sh/ruff/>`_ lint and format,
   `sphinx-lint <https://github.com/sphinx-contrib/sphinx-lint>`_,
   `pyright <https://github.com/microsoft/pyright>`_ (both internal type
   checking and ``--verifytypes`` public API completeness), and the hook that
   regenerates :file:`src/nrtk/utils/_extras.yml` from :file:`pyproject.toml`.
   This replaced the separate ``ruff``, ``pyright`` and ``sphinx``
   environments, so there is one definition of "the checks" rather than one per
   CI job. The environment installs the package with every extra, which the
   ``pyright`` hooks need in order to resolve optional dependencies. The name
   is spelled without a hyphen because tox splits environment names on hyphens
   into factors: ``pre-commit`` would be read as the two factors ``pre`` and
   ``commit`` rather than as a literal name.


How CI Uses Tox
===============

The GitLab CI pipeline uses the same :file:`tox.ini`, ensuring that local and
CI execution are identical. A shared ``.tox-setup`` base
(in :file:`.gitlab-ci/.gitlab-shared.yml`) installs tox and is extended by
both the test and quality stages.

Test Stage
----------

Defined in :file:`.gitlab-ci/.gitlab-test.yml`:

1. **Parallel test matrix** — For each Python version (3.10–3.14), CI runs
   all tox factors in parallel as separate jobs. Each job invokes
   ``tox -e py<version>-<factor>`` and uploads ``.coverage.*``
   artifacts and JUnit XML reports. Jobs are assigned to different runner
   tags based on resource requirements:

   - ``small-cpu``: core, opencv, albumentations, pillow, skimage
   - ``medium-cpu``: pybsm, hcipy, maite, tools, waterdroplet
   - ``autoscaler``: diffusion, optional, doctests, notebooks
   - ``single-gpu``: generative notebook (requires GPU)

2. **Per-version coverage combine** — After all factor jobs for a Python
   version finish, a follow-up job combines their ``.coverage.*`` files
   into a single ``.coverage.<version>`` file.

3. **Final coverage report** — A final job runs ``tox -e coverage`` to
   combine all per-version coverage files, generate a Cobertura XML report,
   and enforce the 90% threshold. This combined report is used by GitLab's
   coverage visualization.

4. **Notebook execution** — Notebooks are run via ``tox -e papermill`` in
   separate jobs, triggered manually on merge requests and automatically on
   scheduled pipelines.

Quality Stage
-------------

Defined in :file:`.gitlab-ci/.gitlab-quality.yml`, this is a single
``precommit`` job running ``tox -e precommit``. Every check lives in
:file:`.pre-commit-config.yaml` — ruff lint and format, sphinx-lint, pyright
internal type checking, and pyright ``--verifytypes`` for public API
completeness — so the same command reproduces CI exactly.


Numba Parallelization Note
--------------------------

The ``pybsm`` and ``waterdroplet`` environments disable ``pytest-xdist``
parallelization by passing ``-n0`` (overriding the default ``-n auto``).
Numba parallelizes with a thread pool inside a single process, so under
``pytest-xdist`` every worker process brings up a pool of its own and the
machine ends up oversubscribed by a factor of the worker count.

That pool is sized from the detected CPU count, which on a workstation means a
test run takes the whole machine even with ``-n0``. ``[testenv]`` lists
``NUMBA_NUM_THREADS`` in ``pass_env``, so capping it is just:

.. prompt:: bash

    NUMBA_NUM_THREADS=4 tox -e py310-waterdroplet

Every environment inherits that ``pass_env``, including the standalone ones.
The cap is worth reaching for even below the core count: capping
``waterdroplet`` at 4 threads took it from 198s to 11s on a 20-core machine.
These tests call many short-lived kernels rather than a few long ones, so the
per-call cost of synchronizing the pool dominates, and that cost grows with the
number of threads in it. ``optional`` and ``doctests`` run the same numba-backed
tests and benefit the same way.


Updating Notebooks Before Committing
=====================================

Jupyter notebooks checked into the repository should have up-to-date cell
outputs and clean metadata. The ``papermill`` tox environment handles both
in a single command — it re-executes every cell and then runs ``nbstripout``
to strip personal metadata (kernel name, execution timestamps, widget state)
while keeping the cell outputs and execution counts intact.

To update a notebook in place, pass the **same path** as both the input and
output arguments:

.. prompt:: bash

    tox -r -e papermill -- docs/examples/end_to_end_overview.ipynb docs/examples/end_to_end_overview.ipynb

.. tip::
   The ``-r`` flag forces tox to recreate the environment. This is used in CI
   to ensure a clean state, but you can omit it locally for faster iteration
   if you haven't changed the ``nrtk`` source since the last run.

Under the hood, this environment:

1. **Builds a local wheel** of ``nrtk`` from the working tree
   (``python -m build --wheel``).
2. **Installs the wheel** with ``--no-index``, so any ``%pip install nrtk``
   commands inside the notebook install the local build instead of pulling
   from PyPI. This ensures notebook outputs reflect your current code.
3. **Executes the notebook** with ``papermill``, which runs every cell top to
   bottom and fails on any exception.
4. **Strips metadata** with ``nbstripout --keep-output --keep-count``,
   removing personal/environment metadata while preserving the rendered
   outputs and execution counts that readers expect to see.

After the command completes, the notebook file is updated in your working
tree. Review the diff and commit it alongside any related code changes.

.. note::
   CI runs notebooks with ``/dev/null`` as the output path — it only
   validates that execution succeeds, it does not update the committed
   notebook. Keeping notebooks up to date is the developer's responsibility
   before pushing.


Practical Tips
==============

- **First run is slow.** Tox creates a fresh virtualenv for every
  environment. Subsequent runs reuse cached environments and are
  significantly faster.
- **Target what you need.** The full matrix spans 5 Python versions × 12
  factors (60 environments). During development, use ``tox -e py310-core``
  or ``tox -f py310`` rather than running the entire matrix.
- **Coverage files.** Each environment writes its coverage data to a
  separate file (``.coverage.<envname>``). Combine them with
  ``tox -e coverage`` before generating a report.
- **Tox is not a Poetry dependency.** Install it separately with
  ``pipx install tox``.
