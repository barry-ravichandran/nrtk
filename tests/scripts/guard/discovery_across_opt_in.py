"""Plugin discovery must find experimental implementations, and only after opting in.

This is the script behind the requirement that ``get_impls()`` not return an empty
set and not depend on what has already been imported. Before this change
``nrtk.impls.perturb_video`` was not registered under ``smqtk_plugins`` and the
experimental gate was read at first import rather than at lookup, so
``PerturbVideo.get_impls()`` came back empty and visibility depended on import order.

Prints five labelled booleans, all expected ``True``, in the order the steps run::

    inert=  hidden_before=  found=  via_entrypoint=  visible_after=

``inert``
    Gate closed, walking every registered entrypoint wakes no experimental
    perturber. Registering the experimental modules must cost ordinary users
    nothing. Runs first, while nothing has opted in.
``hidden_before``
    A gated package imported *before* ``nrtk.experimental`` advertises nothing.
``found``
    Once opted in, discovery returns the perturber -- the "not an empty set" half.
``via_entrypoint``
    Its leaf module was absent from ``sys.modules`` beforehand, so discovery reached
    it through the entrypoint rather than through the import in ``hidden_before``.
    Only meaningful while the leaf is unimported, hence before ``visible_after``.
``visible_after``
    The package imported back in ``hidden_before`` advertises the name now -- the
    "not influenced by import order" half, and what reading the gate at lookup buys.

One script rather than five because each step depends on the state the previous one
left behind. A fresh interpreter because ``tests/conftest.py`` opts in for the whole
suite, so in-process there is no closed gate left to observe.
"""

import sys
import warnings


def main() -> None:
    """Run the sequence and print what each step observed."""
    warnings.simplefilter("ignore")

    from nrtk.interfaces import PerturbImage

    PerturbImage.get_impls()  # walks every registered entrypoint, gate still closed

    import nrtk.impls.perturb_video as perturb_video
    import nrtk.impls.perturb_video.optical as optical

    inert = not any("Perturber" in name for name in dir(perturb_video) + dir(optical))
    hidden_before = "FramewisePerturber" not in dir(perturb_video)

    import nrtk.experimental  # noqa: F401 - opting in is the whole point

    # Sampled before PerturbVideo is pulled in, so the flag below cannot be confused by
    # an import this script did itself. Also keeps a statement between the opt-in and
    # the import that depends on it, where an import sorter could otherwise swap them.
    leaf = "nrtk.impls.perturb_video._framewise_perturber"
    leaf_was_imported = leaf in sys.modules

    from nrtk.interfaces import PerturbVideo

    found = "FramewisePerturber" in {impl.__name__ for impl in PerturbVideo.get_impls()}
    via_entrypoint = not leaf_was_imported and leaf in sys.modules

    visible_after = "FramewisePerturber" in dir(perturb_video)

    print(
        f"inert={inert} hidden_before={hidden_before} found={found} "
        f"via_entrypoint={via_entrypoint} visible_after={visible_after}",
    )


if __name__ == "__main__":
    main()
