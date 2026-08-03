* Fixed the local ``pre-commit`` hooks hard-coding ``poetry run``, which pinned every
  check to one environment regardless of how it was invoked. They are now bare commands,
  so ``tox -e pre-commit`` (what CI runs), ``poetry run pre-commit run --all-files`` and
  the git hook all run the same checks in the environment they were started from.
