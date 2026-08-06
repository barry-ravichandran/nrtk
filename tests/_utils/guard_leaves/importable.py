"""A leaf that imports cleanly, holding stand-ins for two perturbers.

The counterpart to ``missing``: between them they cover the two outcomes the guard
has to handle when binding a symbol. Two classes because binding re-homes a class
globally, so one symbol cannot be claimed by two groups -- the tests need a
distinct name per group.
"""


class Alpha:
    """Stand-in for a perturber with no optional dependency."""


class Beta:
    """Stand-in for a second perturber, declared in a different group."""
