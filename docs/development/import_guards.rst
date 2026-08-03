=============
Import Guards
=============

Most NRTK implementations are conditional: some need an optional dependency (an
"extra"), some are experimental until you opt in, and some are both. Whichever it
is, the class is published from a public module and reported under that path, never
under the private module that defines it. A serialized config records

``nrtk.impls.perturb_image.photometric.blur.GaussianBlurPerturber``

rather than

``nrtk.impls.perturb_image.photometric._blur.gaussian_blur_perturber.GaussianBlurPerturber``

``nrtk._guard.guard()`` provides all of this functionality. Every module that exposes an
implementation calls it exactly once, and nothing else in that module imports.

.. pytestmark: skip

.. code-block:: python

    from nrtk._guard import Group, guard

    if TYPE_CHECKING:
        from nrtk.impls.perturb_image.environment._haze_perturber import HazePerturber as HazePerturber
        from nrtk.impls.perturb_image.environment._water_droplet_perturber import (
            WaterDropletPerturber as WaterDropletPerturber,
        )

    __getattr__: Callable[[str], Any]
    __dir__: Callable[[], list[str]]
    __all__: list[str]

    __getattr__, __dir__, __all__ = guard(
        namespace=globals(),
        groups=[
            Group(symbols={"HazePerturber": "nrtk.impls.perturb_image.environment._haze_perturber"}),
            Group(
                symbols={"WaterDropletPerturber": "nrtk.impls.perturb_image.environment._water_droplet_perturber"},
                extras=["waterdroplet"],
            ),
        ],
    )

Terminology
===========

**package**
    A directory with an ``__init__.py``. A *public* package is one users import
    from; a *private* one starts with an underscore and exists only to hold leaf
    modules.

**leaf module**
    The ``.py`` file that actually defines a class, and what ``symbols`` points at.
    Never a package. Both layouts in the codebase produce one: a private leaf
    inside a public package
    (``nrtk.impls.perturb_image.environment._haze_perturber``), or a public module
    fronting a private package of leaves
    (``nrtk.impls.perturb_image.photometric.blur`` fronting
    ``nrtk.impls.perturb_image.photometric._blur.gaussian_blur_perturber``).

**submodule**
    A module named relative to the package containing it, which is why ``guard()``
    takes ``submodules=``. Use it only when the parent is the point; otherwise say
    module.

**group**
    One ``Group``: the symbols that share the same set of requirements. Add
    ``extras=`` and ``experimental=True`` as the requirements need. Multiple
    extras is still one group — ``extras=["maite", "tools"]`` means both are
    required, not that two groups are needed. A module declares as many groups as
    it has distinct sets of requirements.

``symbols`` maps the public name to the leaf module. Write that path out in full;
hoist a shared prefix into a ``_CONSTANT`` only when the line would otherwise run
past the 120-character limit.

Adding an implementation
========================

Add the class to the ``symbols`` of the group with matching requirements, or create
a new group if existing ones do not satisfy requirements, and add it to the ``if TYPE_CHECKING:`` block.

The ``if TYPE_CHECKING:`` block is not decoration. ``__getattr__: Callable[[str], Any]`` makes pyright
treat every attribute of a guarded module as ``Any``, so a symbol missing from the
block still imports, still type-checks, and still scores 100% on
``--verifytypes`` — it just silently loses its signature, and with it argument
checking at every call site, ``@override`` resolution, and editor hover.
``tests/test_guard.py::test_every_guarded_symbol_has_a_type_checking_import`` is
the only thing that catches it. The bare annotations above the ``guard()`` call
matter too:

.. pytestmark: skip

.. code-block:: python

    __getattr__: Callable[[str], Any]
    __dir__: Callable[[], list[str]]
    __all__: list[str]

``--verifytypes`` requires a declared type for every exported module-level symbol.
Without these it reports ``__getattr__`` and ``__dir__`` as ambiguous rather than
known, which drops the score below 100% and fails. ``__all__`` is not counted
either way; it is declared alongside them so the three read as one unit.

Describing extras
=================

``extras`` is a list of all dependencies required for a ``Group``; a nested tuple indicates a
choice between two or more alternatives, i.e., one of the tuple alternatives must be available at runtime.

.. pytestmark: skip

.. code-block:: python

    extras=["pybsm"]                                     # pybsm
    extras=["maite", "tools"]                            # maite and tools
    extras=[("graphics", "headless")]                    # either OpenCV build
    extras=["albumentations", ("graphics", "headless")]  # albumentations, plus either OpenCV build

The guard renders these requirements into the error that the user sees, with one ``pip install`` per
possibility of meeting the requirements. Requirements are specified as a list rather than a string because
there is no pip syntax for the "and either of these" situation that nested tuples cause.

Rules
=====

**Point at leaf modules, never at anything that runs its own guard.** A public
package like ``nrtk.impls.perturb_image.environment`` and a public module like
``nrtk.impls.perturb_image.photometric.blur`` both call ``guard()``, so resolving a
symbol through either would need that call to have completed first, reintroducing
the import-order dependence the guard exists to remove.

**A private package's** ``__init__.py`` **holds nothing but a docstring.**
Re-exporting an extras-dependent leaf creates a second, unguarded path to the class
and breaks the compliance walk that imports every package with no extras installed.

**Never let** ``__dir__`` **advertise a name that** ``__getattr__`` **would raise on.**
smqtk's plugin discovery calls ``getattr`` on every name ``dir()`` returns and
catches nothing, so a single raising name aborts the entire discovery pass.

This rule is what forces the two different resolution strategies. Extras resolve
eagerly, at ``guard()`` time: whether an extra is installed cannot change
mid-process, so a group whose extra is missing is never advertised in the first
place. Experimental symbols resolve lazily, at lookup time: ``nrtk.experimental``
may be imported long after the module is, so ``__dir__`` has to re-check the gate
on every call.

Registering for discovery
=========================

Being importable is not being discoverable. Register the module that calls
``guard()`` and advertises the class — the same public path the class is published
under — never the leaf module and never a parent that only re-exports. For
``HazePerturber`` that is ``nrtk.impls.perturb_image.environment``, not
``...environment._haze_perturber`` and not ``nrtk.impls.perturb_image``. Every
entry already in ``pyproject.toml`` has that shape:

.. code-block:: toml

    [project.entry-points."smqtk_plugins"]
    "nrtk.impls.perturb_image.environment" = "nrtk.impls.perturb_image.environment"

Registering an experimental module costs nothing while the gate is closed: its
``__dir__`` advertises nothing, so discovery never reaches a gated name.
