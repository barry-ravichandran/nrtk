* Added support for factories with FMV perturbers via a new Generic ``PerturbFactory`` interface. Implementations
  can be found at ``nrtk.impls.perturb_factory``.

* The ``PerturbImageFactory`` interface is now deprecated. A drop in replacement is available via
  ``nrtk.interfaces.PerturbFactory``. Previous ``PerturbImageFactory`` implementations are correspondingly deprecated
  and drop in replacements of the same names can be found at ``nrtk.impls.perturb_factory``. The deprecated classes
  will not be removed until a major release of NRTK, but users are encouraged to utilize the replacement classes as
  soon as feasible.

* Fixed ``PerturbImageFactory.get_default_config()`` returning a non-default value for the ``perturber`` parameter.
  This parameter no longer reports a default value, consistent with the constructor.

* Deprecated attributes that were inadventently advertised as public in ``PerturbFactory`` classes. This requires
  temporarily exposing some of these via properties.

* Added missing ``_create_perturber`` test to the factory mixin class.

* Fixed a few docstrings where an attribute was misnamed.
