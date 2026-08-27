* Added ``retry: 1`` to the shared CI job template, so transient runner failures no longer
  need a manual re-run. ``publish`` opts out, since publishing is not idempotent.
