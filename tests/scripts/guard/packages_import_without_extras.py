"""Every package under ``nrtk`` must import with no optional dependency installed.

Nothing here concerns plugin discovery; that is ``discovery_across_opt_in``. This is
the DSO compliance walk, which imports every package, so none of them may need an
extra to be importable. It is what forces the guard to point at *leaf* modules: a
private ``__init__`` that re-exports an extras-dependent leaf fails here.

The two do touch. smqtk loads every registered entrypoint in a bare loop, so one
unimportable module takes down the whole discovery pass rather than just its own
entry -- importing cleanly is upstream of ``get_impls()`` working at all.

Blocking uses a meta-path finder rather than the absence of the packages, so the
check is real in the all-extras environment too, where they are installed. Prints
``all packages import`` on success, or the list of failures.
"""

import importlib
import pathlib
import sys
import warnings

BLOCKED = {
    "av",
    "click",
    "cv2",
    "diffusers",
    "accelerate",
    "fastapi",
    "hcipy",
    "kwcoco",
    "maite",
    "numba",
    "nrtk_albumentations",
    "PIL",
    "pybsm",
    "pydantic",
    "pydantic_settings",
    "pythonjsonlogger",
    "scipy",
    "skimage",
    "torch",
    "transformers",
    "uvicorn",
}


class Blocker:
    """Meta-path finder that makes every package in :data:`BLOCKED` unimportable."""

    def find_spec(self, fullname: str, _path: object = None, _target: object = None) -> None:
        """Raise for a blocked top-level package, otherwise defer to the next finder.

        ``find_spec``, not the legacy ``find_module``: that protocol was removed in
        3.12, so a ``find_module``-based blocker is ignored there and proves nothing.
        """
        root = fullname.split(".")[0]
        if root in BLOCKED:
            raise ModuleNotFoundError(f"No module named {root!r}")
        return None  # noqa: RET501 - the finder protocol wants an explicit "not mine"


def main() -> None:
    """Install the blocker, then import every nrtk package and report the failures."""
    warnings.simplefilter("ignore")
    sys.meta_path.insert(0, Blocker())

    try:
        importlib.import_module(sorted(BLOCKED)[0])
    except ModuleNotFoundError:
        pass
    else:
        print("blocker is inert -- this check would be vacuous")
        return

    src = pathlib.Path("src/nrtk")
    names = ["nrtk"] + sorted(
        ".".join(("nrtk", *path.parent.relative_to(src).parts))
        for path in src.rglob("__init__.py")
        if path.parent != src
    )
    failed = [report for name in names if (report := _import_failure(name))]
    print(failed or "all packages import")


def _import_failure(name: str) -> str:
    """Import *name*, returning a description of what went wrong or "" if it worked."""
    try:
        importlib.import_module(name)
    except Exception as ex:  # noqa: BLE001 - any failure to import is a failure to report
        return f"{name}: {type(ex).__name__}: {ex}"
    return ""


if __name__ == "__main__":
    main()
