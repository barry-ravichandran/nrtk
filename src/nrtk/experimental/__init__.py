"""Enable NRTK's experimental features.

Importing this globally enables all experimental features. Experimental APIs can
change or disappear without a deprecation warning. Once enabled, experimental
features can be imported from their usual/stable locations::

    import nrtk.experimental  # noqa: F401
    from nrtk.interfaces import SomeExperimentalInterface
    from nrtk.impls.<subpackage> import SomeExperimentalImpl

Some also need their own extras, installed like any other NRTK extra.
"""

import warnings

from nrtk import _experimental
from nrtk._experimental import ExperimentalWarning as ExperimentalWarning

_experimental.enabled = True

# Warned once here rather than once per symbol on access. Plugin discovery getattrs
# every name ``__dir__`` advertises, so a per-symbol warning fired on every
# ``get_impls()`` call, naming classes the caller had never asked for.
warnings.warn(
    message="Experimental NRTK features are now enabled. Their APIs may change without a deprecation warning.",
    category=ExperimentalWarning,
    stacklevel=2,
)
