* Relaxed the ``maite`` optional dependency pin from ``>=0.9.5,<0.10.0`` to
  ``>=0.9.5,<1.0.0``.

* ``maite`` 0.10.0 made a frame's ``time_s`` optional. ``VideoFrame`` still requires a
  timestamp, so the conversion now raises on a missing one.
