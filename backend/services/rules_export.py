"""
Rules export service for creating detailed rule overviews (CSV format).
Allows filtering by active status and single report or all reports.
"""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, Iterable, List, Literal, Optional


RuleStatusFilter = Literal["active", "inactive", "both"]


def _escape_csv_field(value: Any) -> str:
    """Safely escape a field for CSV output."""
    text = str(value or "").strip()
    return text


def _build_condition_preview(rule: Dict[str, Any]) -> str:
    """Extract a readable condition preview from rule."""
    # Try multiple common condition field names
    for field in ["condition", "sql", "formula", "check"]:
        if field in rule and rule[field]:
            preview = str(rule[field]).strip()
            if preview:
                # Limit to 200 chars for readability
                return preview[:200]
    return ""


def iter_rule_rows(
    report_models: Iterable[Dict[str, Any]],
    report_id_filter: Optional[str] = None,
    status_filter: RuleStatusFilter = "both",
) -> Iterable[Dict[str, str]]:
    """
    Iterate over all rules with their report and field context.
    
    Args:
        report_models: Iterable of report model dicts with 'report', 'model', 'source' keys
        report_id_filter: If set, only yield rules from this report ID
        status_filter: "active", "inactive", or "both"
    
    Yields:
        Dict with keys: report_name, report_id, field_name, field_internal_name,
                       rule_message, rule_status, dq_type, rule_type, condition, source
    """
    for item in report_models:
        report_dict = dict(item.get("report") or {})
        model_dict = item.get("model") or {}
        source = item.get("source") or "nemo"
        
        report_id = str(
            report_dict.get("internalName")
            or report_dict.get("id")
            or report_dict.get("displayName")
            or ""
        ).strip()
        
        report_name = report_dict.get("displayName") or report_id
        
        # Skip if filtered by report
        if report_id_filter and report_id != report_id_filter:
            continue
        
        checks = model_dict.get("checks") or {}
        groups = checks.get("groups") or []
        
        for group in groups:
            field_name = group.get("displayName") or group.get("internalName") or ""
            field_internal_name = group.get("internalName") or field_name
            
            rules = group.get("rules") or []
            
            # If group has no rules, yield a single entry showing no rules
            if not rules:
                yield {
                    "report_name": report_name,
                    "report_id": report_id,
                    "field_name": field_name,
                    "field_internal_name": field_internal_name,
                    "rule_message": "(keine Regeln)",
                    "rule_status": "",
                    "dq_type": "",
                    "rule_type": "",
                    "condition": "",
                    "source": "Entwurf" if source == "draft" else "NEMO",
                }
                continue
            
            for rule in rules:
                is_active = bool(rule.get("active"))
                
                # Apply status filter
                if status_filter == "active" and not is_active:
                    continue
                if status_filter == "inactive" and is_active:
                    continue
                
                rule_message = rule.get("message") or ""
                dq_type = rule.get("dimension") or ""
                rule_type = rule.get("ruleType") or rule.get("type") or ""
                condition = _build_condition_preview(rule)
                
                yield {
                    "report_name": report_name,
                    "report_id": report_id,
                    "field_name": field_name,
                    "field_internal_name": field_internal_name,
                    "rule_message": rule_message,
                    "rule_status": "Aktiv" if is_active else "Inaktiv",
                    "dq_type": dq_type,
                    "rule_type": rule_type,
                    "condition": condition,
                    "source": "Entwurf" if source == "draft" else "NEMO",
                }


def build_rules_csv(
    report_models: Iterable[Dict[str, Any]],
    report_id_filter: Optional[str] = None,
    status_filter: RuleStatusFilter = "both",
    language: str = "de",
) -> str:
    """
    Build a CSV string with detailed rule overview.
    
    Args:
        report_models: Iterable of report model dicts
        report_id_filter: Optional report ID to filter by
        status_filter: "active", "inactive", or "both"
        language: Language for headers ("de" or "en")
    
    Returns:
        CSV string (UTF-8 with BOM for Excel compatibility)
    """
    if language == "en":
        headers = [
            "Report",
            "Report ID",
            "Rule group / Field",
            "Field ID",
            "Rule / Error message",
            "Status",
            "DQ type",
            "Rule type",
            "Condition",
            "Source",
        ]
    else:
        headers = [
            "Bericht",
            "Bericht-ID",
            "Regelgruppe / Feld",
            "Feld-ID",
            "Regel / Fehlermeldung",
            "Status",
            "DQ-Typ",
            "Regeltyp",
            "Bedingung",
            "Quelle",
        ]
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    
    # Write headers
    writer.writerow(headers)
    
    # Write data rows
    for row_dict in iter_rule_rows(report_models, report_id_filter, status_filter):
        writer.writerow([
            _escape_csv_field(row_dict["report_name"]),
            _escape_csv_field(row_dict["report_id"]),
            _escape_csv_field(row_dict["field_name"]),
            _escape_csv_field(row_dict["field_internal_name"]),
            _escape_csv_field(row_dict["rule_message"]),
            _escape_csv_field(row_dict["rule_status"]),
            _escape_csv_field(row_dict["dq_type"]),
            _escape_csv_field(row_dict["rule_type"]),
            _escape_csv_field(row_dict["condition"]),
            _escape_csv_field(row_dict["source"]),
        ])
    
    csv_content = output.getvalue()
    return csv_content
