"""
Field cascader: builds cascaded rule output per field in different target formats.

For MSSQL: produces a CASE WHEN ... END expression returning the first matching
           rule message for a field.
For InfoZoom: produces a text description of cascaded rules for a field attribute.

Includes persistent caching of translations to avoid re-computation and error logging.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import logging

from backend.export_connectors.utils.condition_translator import ConditionTranslator
from backend.export_connectors.utils.rule_translation_cache import RuleTranslationCache

_translator = ConditionTranslator()
_cache = RuleTranslationCache()

log = logging.getLogger(__name__)


class FieldCascader:
    """Build cascaded rule output for a single field."""

    def build_cascade_mssql(
        self,
        field: str,
        rules: List[Dict[str, Any]],
    ) -> Tuple[str, List[str]]:
        """
        Build a T-SQL CASE WHEN expression for a field's rules (active rules only).

        Uses persistent cache to avoid re-translating the same rules.

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
            rule_id = rule.get("id", f"{field}_rule")

            if not condition:
                lines.append(f"    -- Skipped (no condition): {message[:80]}")
                continue

            # Try cache first
            cached_sql = _cache.lookup(condition, field)
            if cached_sql:
                log.debug(f"Using cached SQL for {rule_id}")
                if dimension:
                    lines.append(f"    -- {_clean(dimension)}")
                lines.append(f"    WHEN {cached_sql}")
                safe_message = message.replace("'", "''")
                lines.append(f"        THEN N'{safe_message}'")
                continue

            # Translate
            try:
                translated, warning = _translator.to_mssql(condition)
                
                if warning:
                    label = (message or condition)[:60]
                    warnings.append(f"'{label}': {warning}")
                
                # Store in cache
                _cache.store(
                    condition=condition,
                    field=field,
                    expression_infozoom=translated,
                    rule_id=rule_id,
                    message=message,
                )
                
                if dimension:
                    lines.append(f"    -- {_clean(dimension)}")
                lines.append(f"    WHEN {translated}")
                safe_message = message.replace("'", "''")
                lines.append(f"        THEN N'{safe_message}'")
            except Exception as exc:
                # Log error and skip this rule
                error_msg = f"Translation failed: {type(exc).__name__}: {str(exc)[:100]}"
                _cache.log_error(
                    rule_id=rule_id,
                    error=error_msg,
                    condition=condition,
                    field=field,
                    message=message,
                )
                
                log.warning(f"Skipping {rule_id} due to: {error_msg}")
                lines.append(f"    -- Skipped (translation error): {error_msg[:70]}")
                warnings.append(f"Translation error for {rule_id}: {error_msg}")

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

        Uses persistent cache to avoid re-translating the same rules.

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
            rule_id = rule.get("id", f"{field}_rule_{i}")

            if not condition:
                lines.append(f"{i}. (no condition): '{message}'")
                continue

            # Try cache first
            cached_description = _cache.lookup(condition, field)
            if cached_description:
                log.debug(f"Using cached description for {rule_id}")
                dim_label = f" [{dimension}]" if dimension else ""
                lines.append(f"{i}. IF {cached_description}{dim_label}: THEN '{message}'")
                continue

            # Translate
            try:
                description = _translator.to_description_en(condition, field)
                
                # Store in cache for next time
                _cache.store(
                    condition=condition,
                    field=field,
                    expression_infozoom=description,
                    rule_id=rule_id,
                    message=message,
                )
                
                dim_label = f" [{dimension}]" if dimension else ""
                lines.append(f"{i}. IF {description}{dim_label}: THEN '{message}'")
            except Exception as exc:
                # Log error and use fallback
                error_msg = f"Translation failed: {type(exc).__name__}: {str(exc)[:100]}"
                _cache.log_error(
                    rule_id=rule_id,
                    error=error_msg,
                    condition=condition,
                    field=field,
                    message=message,
                )
                
                # Use condition as-is as fallback
                log.warning(f"Using fallback for {rule_id}: {error_msg}")
                lines.append(f"{i}. IF {condition}: THEN '{message}'")
                warnings.append(f"Translation error for {rule_id}: {error_msg}")

        if len(effective_rules) > 1:
            lines.append("(Rules evaluated in order; first match wins)")

        return "\n".join(lines), warnings
