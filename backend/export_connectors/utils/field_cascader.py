"""
Field cascader: builds cascaded rule output per field in different target formats.

For MSSQL: produces a CASE WHEN ... END expression returning the first matching
           rule message for a field.
For InfoZoom: produces a text description of cascaded rules for a field attribute.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.export_connectors.utils.condition_translator import ConditionTranslator

_translator = ConditionTranslator()


class FieldCascader:
    """Build cascaded rule output for a single field."""

    def build_cascade_mssql(
        self,
        field: str,
        rules: List[Dict[str, Any]],
    ) -> Tuple[str, List[str]]:
        """
        Build a T-SQL CASE WHEN expression for a field's rules (active rules only).

        Args:
            field: Internal field name (used in comments)
            rules: List of rule dicts (with condition, message, active, dimension)

        Returns:
            (case_when_sql, list_of_warnings)
        """
        import re as _re

        def _clean(v: str) -> str:
            return _re.sub(r"\s+", " ", str(v or "")).strip().replace("--", "-")

        lines: list[str] = ["CASE"]
        warnings: list[str] = []

        for rule in rules:
            if not rule.get("active"):
                continue
            condition = str(rule.get("condition") or "").strip()
            message = str(rule.get("message") or "").strip()
            dimension = str(rule.get("dimension") or "").strip()

            if not condition:
                lines.append(f"    -- Skipped (no condition): {message[:80]}")
                continue

            translated, warning = _translator.to_mssql(condition)
            if warning:
                label = (message or condition)[:60]
                warnings.append(f"'{label}': {warning}")

            if dimension:
                lines.append(f"    -- {_clean(dimension)}")
            lines.append(f"    WHEN {translated}")
            safe_message = message.replace("'", "''")
            lines.append(f"        THEN N'{safe_message}'")

        lines.extend(["    ELSE N''", "END"])
        return "\n".join(lines), warnings

    def build_cascade_infozoom(
        self,
        field: str,
        rules: List[Dict[str, Any]],
        language: str = "en",
        active_only: bool = True,
    ) -> Tuple[str, List[str]]:
        """
        Build a text description of cascaded rules for InfoZoom.

        Args:
            field: Internal field name
            rules: All rules for this group
            language: Language for descriptions
            active_only: If True, skip inactive rules (default); set False when caller
                         has already pre-filtered to include inactive rules.

        Returns:
            (text_description, list_of_warnings)
        """
        lines: list[str] = []
        warnings: list[str] = []

        effective_rules = [r for r in rules if r.get("active")] if active_only else rules
        if not effective_rules:
            return "(no active validation rules)", warnings

        for i, rule in enumerate(effective_rules, start=1):
            condition = str(rule.get("condition") or "").strip()
            message = str(rule.get("message") or "").strip()
            dimension = str(rule.get("dimension") or "").strip()

            description = _translator.to_description_en(condition, field) if condition else message or "(no condition)"

            dim_label = f" [{dimension}]" if dimension else ""
            lines.append(f"{i}. IF {description}{dim_label}: THEN '{message}'")

        if len(effective_rules) > 1:
            lines.append("(Rules evaluated in order; first match wins)")

        return "\n".join(lines), warnings
