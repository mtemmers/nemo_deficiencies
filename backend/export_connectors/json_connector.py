"""
JSON Export Connector.

Exports the rule set as a structured JSON document (definition metadata only,
no cascade/execution logic).  Suitable for documentation, downstream system
integration, and machine-readable rule archives.

Output schema (version 1.0)::

    {
        "version": "1.0",
        "format": "nemo-rules-json",
        "generatedAt": "<ISO timestamp>",
        "report": {"id": ..., "displayName": ..., "internalName": ...},
        "summary": {"totalGroups": N, "totalRules": N, "activeRules": N, "inactiveRules": N},
        "groups": [
            {
                "id": ...,
                "number": N,
                "displayName": ...,
                "internalName": ...,
                "field": ...,
                "description": ...,
                "typeHints": [...],
                "rules": [
                    {
                        "id": ...,
                        "number": N,
                        "active": true/false,
                        "dimension": ...,
                        "ruleType": ...,
                        "message": ...,
                        "condition": ...,
                    },
                    ...
                ]
            },
            ...
        ]
    }
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.export_connectors.base import ExportConnector
from backend.export_connectors import register_connector


class JSONExportConnector(ExportConnector):
    name = "json"
    display_name = "JSON (Regelmetadaten)"
    description = "Exportiert Regelmetadaten als strukturiertes JSON-Dokument (kein ausführbares SQL)."
    version = "1.0"
    file_extension = "json"

    def validate(self, model: Dict[str, Any]) -> List[str]:
        # JSON export is always possible
        return []

    def export(self, model: Dict[str, Any], options: Dict[str, Any] | None = None) -> str:
        options = options or {}
        report = model.get("report") or {}
        groups_raw = ((model.get("checks") or {}).get("groups") or [])
        # Use pre-computed summary when available (set by normalize_editor_model in the API layer).
        # Fall back to counting manually for standalone/test usage.
        pre_summary = model.get("summary") or {}

        groups: list[dict] = []
        total_rules = 0
        active_rules = 0
        inactive_rules = 0

        for group in groups_raw:
            rules_raw = group.get("rules") or []
            rules: list[dict] = []
            for rule in rules_raw:
                is_active = bool(rule.get("active"))
                rules.append({
                    "id": str(rule.get("id") or ""),
                    "number": int(rule.get("number") or 0),
                    "active": is_active,
                    "dimension": str(rule.get("dimension") or ""),
                    "ruleType": str(rule.get("ruleType") or ""),
                    "message": str(rule.get("message") or ""),
                    "condition": str(rule.get("condition") or ""),
                })
                total_rules += 1
                if is_active:
                    active_rules += 1
                else:
                    inactive_rules += 1

            groups.append({
                "id": str(group.get("id") or ""),
                "number": int(group.get("number") or 0),
                "displayName": str(group.get("displayName") or group.get("title") or ""),
                "internalName": str(group.get("internalName") or group.get("field") or ""),
                "field": str(group.get("field") or ""),
                "description": str(group.get("description") or ""),
                "typeHints": list(group.get("typeHints") or []),
                "rules": rules,
            })

        payload: Dict[str, Any] = {
            "version": "1.0",
            "format": "nemo-rules-json",
            "generatedAt": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
            "report": {
                "id": str(report.get("id") or ""),
                "displayName": str(report.get("displayName") or ""),
                "internalName": str(report.get("internalName") or ""),
            },
            "summary": {
                "totalGroups": len(groups),
                # Prefer pre-computed counts from normalize_editor_model to avoid drift.
                "totalRules": pre_summary.get("ruleCount", total_rules),
                "activeRules": pre_summary.get("activeRuleCount", active_rules),
                "inactiveRules": pre_summary.get("inactiveRuleCount", inactive_rules),
            },
            "groups": groups,
        }

        indent = int(options.get("indent", 2))
        return json.dumps(payload, ensure_ascii=False, indent=indent)


register_connector("json", JSONExportConnector)
