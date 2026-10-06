"""
Base class and registry for export connectors.
All export connectors must extend ExportConnector and call register_connector().
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ExportConnectorError(Exception):
    """Raised when an export connector encounters an unrecoverable error."""
    pass


class ExportConnector(ABC):
    """Base class for all export connectors."""

    # Metadata – override in subclass
    name: str = ""                    # e.g. "mssql", "json", "infozoom"
    display_name: str = ""            # e.g. "Microsoft SQL Server (T-SQL)"
    description: str = ""
    version: str = "1.0"
    file_extension: str = "txt"       # default extension for download filename

    @abstractmethod
    def validate(self, model: Dict[str, Any]) -> List[str]:
        """
        Validate whether the model is exportable.

        Returns:
            List of warning strings (empty if everything is OK).
        """

    @abstractmethod
    def export(self, model: Dict[str, Any], options: Dict[str, Any] | None = None) -> str:
        """
        Export the model into the target format.

        Args:
            model: Editor model (with checks.groups, source.attributes, etc.)
            options: Format-specific options

        Returns:
            Export string (SQL, JSON, text, etc.)

        Raises:
            ExportConnectorError: for unrecoverable errors.
        """

    def get_options_schema(self) -> Dict[str, Any]:
        """
        Optional: Return a schema for format-specific UI options.
        e.g. {"mode": {"type": "select", "options": ["create_and_insert", "insert_only"]}}
        """
        return {}
