"""A stand-in plugin interface, so discovery can be tested without a real one.

Subclasses NRTK's :class:`Plugfigurable` rather than smqtk's, because that is where
the fault-tolerant entrypoint loading and the private-implementation filter live --
the behaviour under test.

``PLUGIN_NAMESPACE`` is inherited as ``smqtk_plugins``, which is what lets a
synthetic distribution register an implementation of this interface.
"""

from nrtk.interfaces._plugfigurable import Plugfigurable


class GuardedThing(Plugfigurable):
    """Stand-in for an interface like ``PerturbImage``, with nothing else attached."""
