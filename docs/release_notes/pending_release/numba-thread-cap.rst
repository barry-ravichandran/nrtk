* Added ``NUMBA_NUM_THREADS`` to ``pass_env`` in :file:`tox.ini`, so the numba-backed
  environments can be kept from claiming every core. Without it tox drops the variable
  silently.
