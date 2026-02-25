* Added a ``UserWarning`` in ``WaterDropletPerturber`` when ``size_range`` values are
  below the minimum effective droplet size of ``0.1``. The water droplet model enforces
  a minimum droplet radius of ``0.1`` in glass coordinate units; values below this
  threshold are clamped to ``0.1``. Updated docstrings to document this constraint and
  advise using ``num_drops`` to control the number of droplets instead.

* Added ``test_size_range_below_minimum_warns`` and ``test_size_range_above_minimum_no_warning``
  to ``TestWaterDropletPerturber`` to verify the new warning behavior.
