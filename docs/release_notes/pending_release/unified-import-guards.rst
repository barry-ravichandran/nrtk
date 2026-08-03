* Replaced the four hand-written import-guard patterns with a single helper,
  ``nrtk._guard.guard``, and retrofitted every implementation module onto it. A module
  now declares what it exposes as one ``Group`` per set of requirements, covering stable and
  experimental implementations, with or without extras, in the same way. The same call
  also attaches lazily-imported submodules, so every module in ``nrtk`` that installs
  ``__getattr__``/``__dir__``/``__all__`` now does it the one way, rather than mixing
  ``lazy_loader`` with a hand-written guard. ``lazy-loader`` is consequently no longer
  a dependency.

* Fixed experimental implementations being invisible to ``get_impls()``. The gate is
  now read at lookup time rather than at first import, so ``import nrtk.experimental``
  works regardless of what has already been imported, and ``nrtk.impls.perturb_video``
  and ``nrtk.impls.perturb_video.optical`` are registered as ``smqtk_plugins``
  entrypoints. Both stay inert until experimental features are enabled.

* Changed ``ExperimentalWarning`` to be emitted once, when ``nrtk.experimental`` is
  imported, rather than once per symbol on first access. Plugin discovery calls
  ``getattr`` on every name a module advertises, so a per-symbol warning meant any
  ``get_impls()`` call warned about experimental classes the caller had never asked
  for.

* Fixed ``nrtk.impls.perturb_video.optical._hcipy`` importing its perturber in its
  ``__init__.py``, which made the package unimportable without the ``hcipy`` extra.

* Fixed ``nrtk.impls`` advertising a ``perturb`` submodule that does not exist, and
  never advertising ``perturb_image``.

* Fixed ``nrtk.entrypoints`` not being attached to the ``nrtk`` package, so
  ``import nrtk`` followed by ``nrtk.entrypoints`` raised ``AttributeError`` where
  every other subpackage resolved.

* Fixed ``nrtk.impls.perturb_image.optical.otf.load_default_config`` being dropped from
  ``__all__`` without the ``pybsm`` extra. It reads JSON into a plain dict and needs
  pybsm neither to import nor to call.

* Fixed the reference documentation for ``nrtk_perturber``, which showed a list of
  internal Python methods instead of the function's signature, arguments, and
  description.

* Documented how to add an implementation behind a guard in
  ``docs/development/import_guards.rst``.

.. note::

   With experimental features enabled, ``get_impls()`` now imports the modules that
   experimental implementations are written in, so it lists only the ones you can
   actually use. Nothing changes if you have not opted in.
