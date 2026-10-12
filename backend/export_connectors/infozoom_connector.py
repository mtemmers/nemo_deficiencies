"""
InfoZoom Export Connector.

Supports two export modes:

**text_definition** (default)
    Generates a text-format definition file for manual import into InfoZoom.
    No SDK required.  Output has two sections:

    1. **Structure** – lists every source attribute (base columns) from
       ``source.attributes[]``.
    2. **Derived Attributes** – one derived attribute per check group,
       combining the group's cascaded rules into a readable English
       description.  These map to InfoZoom derived fields that show
       a validation summary per field.

**sdk_native**
    Uses the InfoZoom SDK COM API (pywin32) to create a binary ``.fdb``
    document that can be opened directly in InfoZoom.  Requires:

    - InfoZoom SDK 9.100 installed (``InfoZoom_SDK_x64_2026_de-DE.exe``)
    - ``pywin32`` Python package (``pip install pywin32``)
    - License code in ``INFOZOOM_LICENSE_CODE`` environment variable

    The ``export()`` method is not available for this mode; use
    ``export_to_file()`` instead.  The API endpoint handles the routing.

Output example (text_definition)::

    ================================================================================
    INFOZOOM STRUCTURE DEFINITION
    Report: Customer Master Data
    ================================================================================

    -- BASE ATTRIBUTES --
    ATTRIBUTE: CUSTOMER_ID
    ATTRIBUTE: FIRST_NAME
    ...

    -- DERIVED VALIDATION ATTRIBUTES --
    DERIVED_ATTRIBUTE: CUSTOMER_ID_Validation
      Source field: CUSTOMER_ID
      Validation rules (cascaded):
        1. IF Customer Id is empty (required) [Vollständigkeit]: THEN 'Customer ID is required'
        2. IF Customer Id has leading or trailing whitespace [Einheitlichkeit]: THEN 'Customer ID has whitespace'
      (Rules evaluated in order; first match wins)

    ...
    ================================================================================

Options:
    mode:             "text_definition" (default) | "sdk_native"
    include_inactive: bool (default False) – include inactive rules in output
    license_code:     Override INFOZOOM_LICENSE_CODE env var (sdk_native mode only)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.export_connectors.base import ExportConnector, ExportConnectorError
from backend.export_connectors import register_connector
from backend.export_connectors.utils.field_cascader import FieldCascader
from backend.export_connectors.infozoom_sdk_wrapper import (
    InfoZoomSDKWrapper,
    InfoZoomSDKError,
    InfoZoomSDKNotInstalledError,
    InfoZoomLicenseError,
    FOX_EXTENSION,
    sdk_available,
)

log = logging.getLogger(__name__)
_cascader = FieldCascader()

_MODE_TEXT = "text_definition"
_MODE_SDK = "sdk_native"


class InfoZoomExportConnector(ExportConnector):
    name = "infozoom"
    display_name = "InfoZoom (Struktur + Validierungsattribute)"
    description = "Exportiert Feldstruktur und Validierungsregeln als InfoZoom-Textdefinition oder natives .fox-Dokument."
    version = "2.0"
    file_extension = "txt"  # sdk_native exports use .fox, set directly by the API endpoint

    def get_options_schema(self) -> Dict[str, Any]:
        mode_options = [_MODE_TEXT]
        if sdk_available():
            mode_options.append(_MODE_SDK)

        schema: Dict[str, Any] = {
            "mode": {
                "type": "select",
                "label": "Export-Modus",
                "options": mode_options,
                "default": _MODE_TEXT,
                "descriptions": {
                    _MODE_TEXT: "Textdefinition für manuellen Import (kein SDK erforderlich)",
                    _MODE_SDK: "Natives InfoZoom .fox-Dokument via SDK (SDK + Lizenz erforderlich)",
                },
            },
            "include_inactive": {
                "type": "checkbox",
                "label": "Inaktive Regeln einschließen",
                "default": False,
            },
        }
        if sdk_available():
            schema["license_code"] = {
                "type": "password",
                "label": "InfoZoom Lizenzcode (überschreibt INFOZOOM_LICENSE_CODE)",
                "default": "",
                "placeholder": "V3559-XXXXX-XXXXX-XXXXX-XXXXX",
            }
        return schema

    def validate(self, model: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[str]:
        warnings: list[str] = []
        opts = options or {}
        mode = str(opts.get("mode") or _MODE_TEXT)

        groups = ((model.get("checks") or {}).get("groups") or [])
        if not groups:
            warnings.append("No check groups found in model – output will have no derived attributes.")
        source_attrs = ((model.get("source") or {}).get("attributes") or [])
        if not source_attrs:
            warnings.append("No source attributes found – base attribute section will be empty.")

        if mode == _MODE_SDK:
            if not sdk_available():
                warnings.append(
                    "SDK mode requested but pywin32 is not installed. "
                    "Run: pip install pywin32"
                )
            # We don't try to activate the license here to avoid side effects;
            # that happens lazily in export_to_file().

        return warnings

    def export(self, model: Dict[str, Any], options: Dict[str, Any] | None = None) -> str:
        """
        Export the model as a text definition (mode=text_definition).

        For sdk_native mode, call export_to_file() instead.  If sdk_native
        is requested here it falls back to text_definition with a warning
        header so the existing API endpoint remains functional.
        """
        options = options or {}
        mode = str(options.get("mode") or _MODE_TEXT)

        if mode == _MODE_SDK:
            # Caller should use export_to_file(); we degrade gracefully here.
            log.warning(
                "InfoZoomExportConnector.export() called with mode='sdk_native'. "
                "Use export_to_file() for binary output. Falling back to text_definition."
            )
            header = (
                "# NOTE: sdk_native mode requested but export() returns text only.\n"
                "# Use export_to_file() for a binary .fdb file.\n\n"
            )
            return header + self._export_text(model, options)

        return self._export_text(model, options)

    def _export_text(self, model: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Render the text-format InfoZoom structure definition."""
        include_inactive = bool(options.get("include_inactive", False))

        report = model.get("report") or {}
        report_name = str(
            report.get("displayName") or report.get("internalName") or report.get("id") or "Unnamed"
        )
        source_attrs = ((model.get("source") or {}).get("attributes") or [])
        groups = ((model.get("checks") or {}).get("groups") or [])
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

        lines: list[str] = []

        # ---- Header ----
        lines.extend([
            "=" * 80,
            "INFOZOOM STRUCTURE DEFINITION",
            f"Report: {report_name}",
            f"Generated: {timestamp}",
            "Generator: nemo_deficiencies InfoZoom export connector v2.0",
            "=" * 80,
            "",
        ])

        # ---- Base Attributes ----
        lines.append("-- BASE ATTRIBUTES --")
        lines.append("-- (These map to your InfoZoom base data columns)")
        lines.append("")

        if source_attrs:
            for attr in source_attrs:
                name = str(attr.get("name") or "").strip()
                comment = str(attr.get("comment") or attr.get("displayName") or "").strip()
                if not name:
                    continue
                attr_line = f"ATTRIBUTE: {name}"
                if comment:
                    attr_line += f"  -- {comment}"
                lines.append(attr_line)
        else:
            lines.append("-- (No source attributes defined)")

        lines.append("")

        # ---- Derived Validation Attributes ----
        lines.append("-- DERIVED VALIDATION ATTRIBUTES --")
        lines.append("-- (Add these as derived fields in InfoZoom for DQ validation display)")
        lines.append("")

        all_warnings: list[str] = []

        for group in groups:
            field, display_name, attr_name, cascade_text, warnings = self._build_group_cascade(
                group, include_inactive
            )
            all_warnings.extend(warnings)

            lines.append(f"DERIVED_ATTRIBUTE: {attr_name}")
            if display_name:
                lines.append(f"  Source field: {display_name}")
            if field and field != display_name:
                lines.append(f"  Internal name: {field}")

            type_hints = list(group.get("typeHints") or [])
            if type_hints:
                lines.append(f"  DQ types: {', '.join(type_hints)}")

            description = str(group.get("description") or "").strip()
            if description:
                lines.append(f"  Description: {description}")

            lines.append("  Validation rules (cascaded):")
            for cascade_line in cascade_text.splitlines():
                lines.append(f"    {cascade_line}")
            lines.append("")

        # ---- Warnings ----
        if all_warnings:
            lines.extend([
                "=" * 80,
                "TRANSLATION WARNINGS",
                "=" * 80,
            ])
            for w in all_warnings:
                lines.append(f"WARNING: {w}")
            lines.append("")

        lines.extend([
            "=" * 80,
            "END OF DEFINITION",
            "=" * 80,
        ])

        return "\n".join(lines)

    @staticmethod
    def _clean(value: str) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @staticmethod
    def _build_group_cascade(
        group: Dict[str, Any],
        include_inactive: bool,
    ) -> tuple[str, str, str, str, list[str]]:
        """
        Process a single check group into cascade components.

        Returns
        -------
        tuple of (field, display_name, attr_name, cascade_text, warnings)
        """
        field = str(group.get("internalName") or group.get("field") or "").strip()
        display_name = str(group.get("displayName") or group.get("title") or field or "").strip()
        rules = group.get("rules") or []

        effective_rules = rules if include_inactive else [r for r in rules if r.get("active")]
        attr_name = (
            f"{field}_Validation" if field else f"Group_{group.get('number', '?')}_Validation"
        )

        cascade_text, warnings = _cascader.build_cascade_infozoom(
            field=field or display_name,
            rules=effective_rules,
            active_only=False,  # caller has already applied the active filter above
        )
        return field, display_name, attr_name, cascade_text, warnings

    # ------------------------------------------------------------------
    # SDK Native export
    # ------------------------------------------------------------------

    def export_to_file(
        self,
        model: Dict[str, Any],
        output_path: str | Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """
        Create a native InfoZoom .fdb document using the SDK.

        Parameters
        ----------
        model:
            Normalised editor model dict (checks.groups, source.attributes, …).
        output_path:
            Destination path for the .fdb file.  Parent directory is created
            if it does not exist.
        options:
            Export options.  Recognised keys:
            - ``include_inactive`` (bool, default False)
            - ``license_code`` (str) – overrides ``INFOZOOM_LICENSE_CODE`` env var

        Returns
        -------
        Path
            Resolved path of the written .fdb file.

        Raises
        ------
        ExportConnectorError
            Wraps ``InfoZoomSDKNotInstalledError``, ``InfoZoomLicenseError``,
            and ``InfoZoomSDKError`` with user-friendly messages.
        """
        options = options or {}
        include_inactive = bool(options.get("include_inactive", False))
        license_code = str(options.get("license_code") or "").strip() or None

        report = model.get("report") or {}
        report_name = str(
            report.get("displayName") or report.get("internalName") or report.get("id") or "Unnamed"
        )
        source_attrs = ((model.get("source") or {}).get("attributes") or [])
        groups = ((model.get("checks") or {}).get("groups") or [])

        # Build base attributes list
        base_attrs: List[Dict[str, Any]] = []
        for attr in source_attrs:
            name = str(attr.get("name") or "").strip()
            if not name:
                continue
            comment = str(attr.get("comment") or attr.get("displayName") or "").strip()
            base_attrs.append({"name": name, "comment": comment})

        # Build derived attributes list (one per check group)
        derived_attrs: List[Dict[str, Any]] = []
        for group in groups:
            field, display_name, attr_name, cascade_text, _ = self._build_group_cascade(
                group, include_inactive
            )
            derived_attrs.append({
                "name": attr_name,
                "expression": cascade_text,
                "source": field or display_name,
            })

        # Initialise SDK wrapper — raises ExportConnectorError on failure
        try:
            wrapper = InfoZoomSDKWrapper()
        except InfoZoomSDKNotInstalledError as exc:
            raise ExportConnectorError(
                f"InfoZoom SDK nicht verfügbar: {exc}\n"
                "Bitte das InfoZoom SDK installieren (InfoZoom_SDK_x64_2026_de-DE.exe) "
                "und 'pip install pywin32' ausführen."
            ) from exc
        except InfoZoomLicenseError as exc:
            raise ExportConnectorError(
                f"InfoZoom Lizenzfehler: {exc}\n"
                "Bitte den Lizenzcode in der Umgebungsvariable INFOZOOM_LICENSE_CODE "
                "oder in den Export-Optionen angeben."
            ) from exc

        # Create the document
        try:
            written_path = wrapper.create_document(
                output_path=output_path,
                base_attributes=base_attrs,
                derived_attributes=derived_attrs,
            )
        except InfoZoomSDKError as exc:
            raise ExportConnectorError(
                f"InfoZoom SDK Fehler beim Erstellen des Dokuments: {exc}"
            ) from exc

        return written_path


register_connector("infozoom", InfoZoomExportConnector)
