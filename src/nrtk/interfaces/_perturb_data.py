"""Defines PerturbData, a common interface for implementing data-specific perturber interfaces."""

from __future__ import annotations

__all__ = []

from typing import Any

from typing_extensions import override

from nrtk.interfaces._plugfigurable import Plugfigurable


class PerturbData(Plugfigurable):
    """Abstract base class to perturb various data types."""

    @classmethod
    def get_type_string(cls) -> str:
        """Returns the fully qualified type string of the perturber class.

        Returns:
            A string representing the fully qualified type, in the format `<module>.<class_name>`.
            For example, "my_module.MyCustomPerturber".
        """
        return f"{cls.__module__}.{cls.__name__}"

    @override
    def get_config(self) -> dict[str, Any]:
        """Returns the current configuration of the instance.

        Returns:
            dict[str, Any]: Configuration dictionary with current settings.
        """
        return {}
