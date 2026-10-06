"""
Export connector registry with auto-discovery.

All modules matching ``*_connector.py`` in this package are imported
automatically when the package is first loaded.  Each module is expected
to call :func:`register_connector` so its connector becomes available.

Usage::

    from backend.export_connectors import get_connector, list_connectors

    connector = get_connector("mssql")
    result = connector.export(editor_model, options={"mode": "create_and_insert"})
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Dict, List, Type

from backend.export_connectors.base import ExportConnector, ExportConnectorError  # noqa: F401 – re-export

__all__ = [
    "ExportConnector",
    "ExportConnectorError",
    "register_connector",
    "get_connector",
    "get_connectors",
    "list_connectors",
]

log = logging.getLogger(__name__)

_CONNECTORS: Dict[str, Type[ExportConnector]] = {}


def register_connector(name: str, connector_class: Type[ExportConnector]) -> None:
    """Register a connector under *name*.  Called by each connector module."""
    _CONNECTORS[name] = connector_class
    log.debug("Export connector registered: %s (%s)", name, connector_class.__name__)


def get_connector(name: str) -> ExportConnector:
    """Return an instantiated connector for *name*, or raise KeyError."""
    cls = _CONNECTORS[name]
    return cls()


def get_connectors() -> Dict[str, Type[ExportConnector]]:
    """Return a copy of the full connector registry."""
    return dict(_CONNECTORS)


def list_connectors() -> List[Dict[str, str]]:
    """Return a list of connector metadata dicts suitable for API responses."""
    result = []
    for name, cls in _CONNECTORS.items():
        instance = cls()
        result.append({
            "name": name,
            "displayName": instance.display_name,
            "description": instance.description,
            "version": instance.version,
            "fileExtension": instance.file_extension,
        })
    return result


def _discover_connectors() -> None:
    """Auto-import every ``*_connector.py`` module in this package directory."""
    module_dir = Path(__file__).parent
    for module_file in sorted(module_dir.glob("*_connector.py")):
        if module_file.name.startswith("_"):
            continue
        module_name = module_file.stem
        try:
            importlib.import_module(f"backend.export_connectors.{module_name}")
        except Exception:
            log.exception("Failed to load export connector module: %s", module_name)


_discover_connectors()
