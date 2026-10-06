"""
MSSQL Export Connector.

Generates a T-SQL validation script that mirrors the NEMO/SAP HANA SQL
structure (CTEs + cascaded CASE WHEN), but uses Microsoft SQL Server syntax.

Key translation steps (NEMO HANA → T-SQL):
    LENGTH(x)              → LEN(x)
    TRIM(x)                → LTRIM(RTRIM(x))
    TO_NVARCHAR(x)         → CAST(x AS NVARCHAR(MAX))
    LIKE_REGEXPR(x, pat)   → PATINDEX approximation  [with warning]
    REPLACE_REGEXPR(...)   → manual review required   [with warning]

Options:
    mode:  "create_and_insert"  (default) – emit CREATE TABLE + INSERT
           "insert_only"                  – only INSERT statements

Output structure::

    -- [header with report info and warnings summary]
    -- ================================================================
    -- checks CTE (one CASE WHEN block per rule group)
    -- ================================================================
    -- [optional: CREATE TABLE dbo.RuleValidation ...]
    -- INSERT INTO dbo.RuleValidation SELECT ...
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.export_connectors.base import ExportConnector
from backend.export_connectors import register_connector
from backend.export_connectors.utils.condition_translator import ConditionTranslator
from backend.export_connectors.utils.field_cascader import FieldCascader

_translator = ConditionTranslator()
_cascader = FieldCascader()


class MSSQLExportConnector(ExportConnector):
    name = "mssql"
    display_name = "Microsoft SQL Server (T-SQL)"
    description = "Exportiert das Regelwerk als T-SQL Validierungsskript (CTEs, Cascade)."
    version = "1.0"
    file_extension = "sql"

    def get_options_schema(self) -> Dict[str, Any]:
        return {
            "mode": {
                "type": "select",
                "label": "Export-Modus",
                "options": ["create_and_insert", "insert_only"],
                "default": "create_and_insert",
            }
        }

    def validate(self, model: Dict[str, Any]) -> List[str]:
        warnings: list[str] = []
        groups = ((model.get("checks") or {}).get("groups") or [])
        for group in groups:
            for rule in (group.get("rules") or []):
                if not rule.get("active"):
                    continue
                condition = str(rule.get("condition") or "").strip()
                if not condition:
                    continue
                _, w = _translator.to_mssql(condition)
                if w:
                    msg = str(rule.get("message") or condition)[:60]
                    warnings.append(f"Rule '{msg}': {w}")
        return warnings

    def export(self, model: Dict[str, Any], options: Dict[str, Any] | None = None) -> str:
        options = options or {}
        mode = str(options.get("mode") or "create_and_insert")
        groups = ((model.get("checks") or {}).get("groups") or [])

        # Collect all translation warnings
        all_warnings: list[str] = []
        rendered_groups: list[tuple[str, str]] = []  # (group_title, case_sql)

        for group in groups:
            title = str(group.get("displayName") or group.get("title") or "")
            field = str(group.get("internalName") or group.get("field") or "")
            label = title or field or f"Group {group.get('number', '?')}"
            rules = group.get("rules") or []

            case_lines, group_warnings = self._render_group_case(group, rules)
            all_warnings.extend(group_warnings)
            rendered_groups.append((label, case_lines))

        lines: list[str] = []

        # Header
        lines.extend(self._render_header(model, all_warnings))
        lines.append("")

        # Checks CTE
        lines.append("WITH checks AS (")
        lines.append("    SELECT")
        lines.append("        *,")
        lines.append("        (")

        if rendered_groups:
            for i, (label, case_sql) in enumerate(rendered_groups):
                if i > 0:
                    lines.append("            ||")
                lines.append(f"            -- {self._clean_comment(label)}")
                for cline in case_sql.splitlines():
                    lines.append(f"            {cline}")
        else:
            lines.extend([
                "            CASE",
                "                ELSE ''",
                "            END",
            ])

        lines.extend([
            "        ) AS DEFICIENCY_DESCRIPTION",
            "    FROM your_source_table  -- TODO: replace with actual source",
            ")",
            "",
        ])

        # Optional CREATE TABLE
        if mode == "create_and_insert":
            lines.extend(self._render_create_table())
            lines.append("")

        # INSERT statement
        lines.extend(self._render_insert())
        lines.append("")

        # Warning annotations at the end
        if all_warnings:
            lines.append("-- ================================================================================")
            lines.append("-- TRANSLATION WARNINGS")
            lines.append("-- ================================================================================")
            for w in all_warnings:
                lines.append(f"-- WARNING: {self._clean_comment(w)}")

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Internal render helpers                                               #
    # ------------------------------------------------------------------ #

    def _render_header(self, model: Dict[str, Any], warnings: List[str]) -> list[str]:
        report = model.get("report") or {}
        summary = model.get("summary") or {}
        groups = ((model.get("checks") or {}).get("groups") or [])
        report_name = self._clean_comment(
            report.get("displayName") or report.get("internalName") or report.get("id") or "Unnamed"
        )
        internal_name = self._clean_comment(report.get("internalName") or "")
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        total_rules = summary.get("ruleCount") or sum(len(g.get("rules") or []) for g in groups)
        active_rules = summary.get("activeRuleCount") or sum(
            sum(1 for r in (g.get("rules") or []) if r.get("active"))
            for g in groups
        )
        lines = [
            "-- ================================================================================",
            "-- NEMO DQM Report – Microsoft SQL Server (T-SQL) Export",
            f"-- Report: {report_name}",
        ]
        if internal_name:
            lines.append(f"-- Internal Name: {internal_name}")
        lines.extend([
            f"-- Generated at: {timestamp}",
            "-- Generator: nemo_deficiencies MSSQL export connector v1.0",
            f"-- Check groups: {len(groups)}",
            f"-- Rules (active/total): {active_rules} / {total_rules}",
        ])
        if warnings:
            lines.append(f"-- Translation warnings: {len(warnings)} (see bottom of file)")
        lines.append("-- ================================================================================")
        return lines

    def _render_group_case(
        self,
        group: Dict[str, Any],
        rules: List[Dict[str, Any]],
    ) -> tuple[str, list[str]]:
        """Render a CASE WHEN block for one group via the shared FieldCascader."""
        field = str(group.get("internalName") or group.get("field") or "")
        return _cascader.build_cascade_mssql(field=field, rules=rules)

    def _render_create_table(self) -> list[str]:
        return [
            "-- ================================================================================",
            "-- CREATE TABLE (adjust schema/name as needed)",
            "-- ================================================================================",
            "IF OBJECT_ID(N'dbo.RuleValidation', N'U') IS NULL",
            "BEGIN",
            "    CREATE TABLE dbo.RuleValidation (",
            "        Id              INT           IDENTITY(1,1) PRIMARY KEY,",
            "        RecordKey       NVARCHAR(255) NULL,",
            "        Deficiency      NVARCHAR(MAX) NULL,",
            "        ExportedAt      DATETIME2     DEFAULT GETUTCDATE()",
            "    );",
            "END;",
        ]

    def _render_insert(self) -> list[str]:
        return [
            "-- ================================================================================",
            "-- INSERT validation results",
            "-- ================================================================================",
            "INSERT INTO dbo.RuleValidation (RecordKey, Deficiency)",
            "SELECT",
            "    NULL  AS RecordKey,  -- TODO: replace with your key column",
            "    DEFICIENCY_DESCRIPTION",
            "FROM checks",
            "WHERE DEFICIENCY_DESCRIPTION <> N'';",
        ]

    @staticmethod
    def _clean_comment(value: str) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip().replace("--", "-")


register_connector("mssql", MSSQLExportConnector)
