* Unified how NRTK guards implementations that need an optional dependency (an
  "extra") or an experimental opt-in. Using an implementation whose extra is not
  installed now raises the same style of error everywhere, naming the missing extra
  and the exact ``pip install`` command that provides it. Internally, every module
  now uses one helper, ``nrtk._guard.guard``, in place of four hand-written guard
  patterns, and ``lazy-loader`` is no longer a dependency.

* Fixed experimental implementations being invisible to ``get_impls()``. Enabling
  experimental features now takes effect no matter what was imported first, and the
  experimental video perturbers are now discoverable through ``get_impls()`` once you
  opt in. Until then they stay hidden, as before.

* Changed ``ExperimentalWarning`` to be emitted once, when ``nrtk.experimental`` is
  imported, rather than once per symbol on first access — previously a single
  ``get_impls()`` call could warn about experimental classes the caller had never
  asked for.

* Fixed ``nrtk.impls.perturb_video.optical`` failing to import without the ``hcipy``
  extra installed.

* Fixed ``nrtk.impls`` advertising a ``perturb`` submodule that does not exist, and
  never advertising ``perturb_image``.

* Fixed ``nrtk.entrypoints`` not being attached to the ``nrtk`` package, so
  ``import nrtk`` followed by ``nrtk.entrypoints`` raised ``AttributeError`` where
  every other subpackage resolved.

* Fixed ``nrtk.impls.perturb_image.optical.otf.load_default_config`` being dropped from
  ``__all__`` without the ``pybsm`` extra. It reads JSON into a plain dict and needs
  pybsm neither to import nor to call.

* Fixed ``get_impls()`` returning NRTK's private base classes and helpers alongside
  the real implementations.

* Changed ``FramewisePerturber`` to default ``frame_perturber`` to ``None``, meaning
  frames pass through unchanged, rather than to a private no-op perturber. Behaviour is
  the same, but a default instance's serialized configuration now records ``None`` for
  ``frame_perturber`` instead of that perturber's configuration.

* Fixed the reference documentation for ``nrtk_perturber``, which showed a list of
  internal Python methods instead of the function's signature, arguments, and
  description.

* Documented how to add an implementation behind a guard in
  ``docs/development/import_guards.rst``.

.. note::

   With experimental features enabled, ``get_impls()`` now reports experimental
   implementations, alongside stable implementations. If you have not opted into
   experimental features, only stable implementations will be reported.
