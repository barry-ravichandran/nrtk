* Bumped ``pybsm`` dependency to ``>=0.16.0``.

* Updated ``PybsmPerturber`` to convert simulated photoelectrons to pixels with pyBSM's
  sensor-calibrated radiometric conversion, preserving sensor and scenario-driven brightness/
  contrast effects in the output. A new ``pixel_conversion_mode`` parameter selects the conversion
  with the legacy behavior made available via ``pixel_conversion_mode="minmax"``.

* Updated ``PybsmPerturberMixin`` to only enforce exact atmosphere database values for
  ``altitude`` and ``ground_range`` when ``interp=False``.
