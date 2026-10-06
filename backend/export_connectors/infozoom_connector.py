"""
InfoZoom Export Connector.

Generates a text-format definition file for manual import into InfoZoom.

The output has two sections:
    1. **Structure** – lists every source attribute (base columns) from
       ``source.attributes[]``.
    2. **Derived Attributes** – one derived attribute per check group,
       combining the group's cascaded rules into a readable English
       description.  These map to InfoZoom derived fields that show
       a validation summary per field.

Output example::

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
    include_inactive: bool (default False) – include inactive rules in output
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List

from backend.export_connectors.base import ExportConnector
from backend.export_connectors import register_connector
from backend.export_connectors.utils.field_cascader import FieldCascader

_cascader = FieldCascader()


class InfoZoomExportConnector(ExportConnector):
    name = "infozoom"
    display_name = "InfoZoom (Struktur + Validierungsattribute)"
    description = "Exportiert Feldstruktur und Validierungsregeln als InfoZoom-Textdefinition für manuellen Import."
    version = "1.0"
    file_extension = "txt"

    def get_options_schema(self) -> Dict[str, Any]:
        return {
            "include_inactive": {
                "type": "checkbox",
                "label": "Inaktive Regeln einschließen",
                "default": False,
            }
        }

    def validate(self, model: Dict[str, Any]) -> List[str]:
        warnings: list[str] = []
        groups = ((model.get("checks") or {}).get("groups") or [])
        if not groups:
            warnings.append("No check groups found in model – output will have no derived attributes.")
        source_attrs = ((model.get("source") or {}).get("attributes") or [])
        if not source_attrs:
            warnings.append("No source attributes found – base attribute section will be empty.")
        return warnings

    def export(self, model: Dict[str, Any], options: Dict[str, Any] | None = None) -> str:
        options = options or {}
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
            "Generator: nemo_deficiencies InfoZoom export connector v1.0",
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
            field = str(group.get("internalName") or group.get("field") or "").strip()
            display_name = str(group.get("displayName") or group.get("title") or field or "").strip()
            rules = group.get("rules") or []

            if include_inactive:
                effective_rules = rules
            else:
                effective_rules = [r for r in rules if r.get("active")]

            attr_name = f"{field}_Validation" if field else f"Group_{group.get('number', '?')}_Validation"

            cascade_text, warnings = _cascader.build_cascade_infozoom(
                field=field or display_name,
                rules=effective_rules,
                active_only=False,  # caller has already applied the filter above
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


register_connector("infozoom", InfoZoomExportConnector)
