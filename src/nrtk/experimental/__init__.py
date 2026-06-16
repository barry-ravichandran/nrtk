"""Enable NRTK's experimental features.

Importing this globally enables all experimental features. Experimental APIs can
change or disappear without a deprecation warning. Once enabled, experimental
features can be imported from their usual/stable locations::

    import nrtk.experimental  # noqa: F401
    from nrtk.interfaces import SomeExperimentalInterface
    from nrtk.impls.<subpackage> import SomeExperimentalImpl

Some also need their own extras, installed like any other NRTK extra.
"""

from nrtk import _experimental
from nrtk._experimental import ExperimentalWarning as ExperimentalWarning

_experimental.enabled = True
