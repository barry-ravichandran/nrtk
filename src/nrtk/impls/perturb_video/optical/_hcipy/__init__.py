"""HCIPy-based optical video perturber implementations.

Intentionally empty. Everything here needs the ``hcipy`` extra, so re-exporting a
perturber would be an unguarded path around the guard in
:mod:`nrtk.impls.perturb_video.optical`, and would break the compliance walk that
imports every package with no extras installed.
"""
