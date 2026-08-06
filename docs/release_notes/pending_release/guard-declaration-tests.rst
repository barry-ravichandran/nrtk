* Replaced the per-module ``ImportGuardTestsMixin`` subclasses with
  ``tests/test_guard_declarations.py``, which checks every ``guard()`` call site rather
  than re-testing one shared code path once per module. It verifies that each extra
  named in a ``Group`` really exists, that no symbol is claimed by
  two groups and no class is published from two modules, that the ``if TYPE_CHECKING:``
  block and the declaration agree, and that every declared symbol either resolves or
  raises an ``ImportError`` naming the extras it needs.

* Replaced the per-module canary tests with ``tests/test_guard_canaries.py``, which
  generates one case per ``Group`` that declares extras and carries the marker for those
  extras. Adding an implementation no longer means writing a canary, and every declared
  group now has one — previously three markers were covered by fewer canaries than they
  had groups.

* Added an end-to-end discovery check that runs against a test fixture rather than a
  real implementation, so it tests the guard's machinery rather than whatever NRTK
  currently ships. That a real module is registered for discovery is checked
  directly, by asserting every module publishing implementations has an
  ``smqtk_plugins`` entry.

* Changed import-guard testing to stop simulating missing dependencies. A symbol is
  either importable in a given environment or it is not, so the ``core`` environment now
  covers every "extra is missing" path and ``optional`` covers every "extra is present"
  path, without evicting anything from ``sys.modules``.

* Removed the bespoke import-guard tests for ``TurbulenceVideoPerturber``, which mocked
  ``scipy`` away while keeping ``hcipy`` importable. No supported install produces that
  state: the ``hcipy`` extra pins both, and ``hcipy`` itself requires ``scipy``. Its
  canary is now generated like every other extra's.
