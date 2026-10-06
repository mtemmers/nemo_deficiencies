"""
Tests for the Generic Export Connector Framework.

Tests cover:
- Registry auto-discovery
- JSON connector output schema
- MSSQL connector T-SQL output
- InfoZoom connector text output
- Condition translator (NEMO → T-SQL, NEMO → English description)
- Field cascader helpers
- API endpoint behaviour (via TestClient)
"""

from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from backend.export_connectors import get_connector, get_connectors, list_connectors
from backend.export_connectors.json_connector import JSONExportConnector
from backend.export_connectors.mssql_connector import MSSQLExportConnector
from backend.export_connectors.infozoom_connector import InfoZoomExportConnector
from backend.export_connectors.utils.condition_translator import ConditionTranslator
from backend.export_connectors.utils.field_cascader import FieldCascader


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_model() -> Dict[str, Any]:
    """A minimal but valid editor model with two groups and several rules."""
    return {
        "report": {
            "id": "TEST_REPORT",
            "displayName": "Test Report",
            "internalName": "TEST_REPORT",
        },
        "summary": {
            "checkGroupCount": 2,
            "ruleCount": 4,
            "activeRuleCount": 3,
            "inactiveRuleCount": 1,
        },
        "source": {
            "attributes": [
                {"name": "CUSTOMER_ID", "expression": "CUSTOMER_ID", "comment": "Kundennummer"},
                {"name": "EMAIL", "expression": "EMAIL", "comment": "E-Mail-Adresse"},
                {"name": "ZIP_CODE", "expression": "ZIP_CODE", "comment": "Postleitzahl"},
            ]
        },
        "checks": {
            "groups": [
                {
                    "id": "group_001",
                    "number": 1,
                    "title": "Kundennummer Prüfung",
                    "displayName": "Kundennummer",
                    "internalName": "CUSTOMER_ID",
                    "field": "CUSTOMER_ID",
                    "description": "Prüft ob die Kundennummer vorhanden ist",
                    "typeHints": ["Vollständigkeit"],
                    "rules": [
                        {
                            "id": "group_001_rule_001",
                            "number": 1,
                            "active": True,
                            "dimension": "Vollständigkeit",
                            "ruleType": "completeness",
                            "message": "Kundennummer fehlt",
                            "condition": "CUSTOMER_ID IS NULL",
                        },
                        {
                            "id": "group_001_rule_002",
                            "number": 2,
                            "active": False,
                            "dimension": "Einheitlichkeit",
                            "ruleType": "trim_whitespace",
                            "message": "Kundennummer hat Leerzeichen",
                            "condition": "TRIM(CUSTOMER_ID) <> CUSTOMER_ID",
                        },
                    ],
                },
                {
                    "id": "group_002",
                    "number": 2,
                    "title": "E-Mail Prüfung",
                    "displayName": "E-Mail",
                    "internalName": "EMAIL",
                    "field": "EMAIL",
                    "description": "",
                    "typeHints": ["Validität"],
                    "rules": [
                        {
                            "id": "group_002_rule_001",
                            "number": 1,
                            "active": True,
                            "dimension": "Vollständigkeit",
                            "ruleType": "completeness",
                            "message": "E-Mail fehlt",
                            "condition": "EMAIL IS NULL",
                        },
                        {
                            "id": "group_002_rule_002",
                            "number": 2,
                            "active": True,
                            "dimension": "Validität",
                            "ruleType": "regex",
                            "message": "E-Mail Format ungültig",
                            "condition": "EMAIL NOT LIKE '%@%.%'",
                        },
                    ],
                },
            ]
        },
    }


@pytest.fixture()
def model_with_nemo_syntax(minimal_model) -> Dict[str, Any]:
    """Model that includes NEMO-specific SQL functions (for translation tests)."""
    model = dict(minimal_model)
    model["checks"]["groups"][0]["rules"].append({
        "id": "group_001_rule_003",
        "number": 3,
        "active": True,
        "dimension": "Korrektheit",
        "ruleType": "regex",
        "message": "Nur Buchstaben erlaubt",
        "condition": "CUSTOMER_ID LIKE_REGEXPR('[\\P{L}]')",
    })
    model["checks"]["groups"][0]["rules"].append({
        "id": "group_001_rule_004",
        "number": 4,
        "active": True,
        "dimension": "Korrektheit",
        "ruleType": "max_length",
        "message": "Kundennummer zu lang",
        "condition": "LENGTH(CUSTOMER_ID) > 20",
    })
    return model


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_known_connectors_registered(self):
        connectors = get_connectors()
        assert "json" in connectors
        assert "mssql" in connectors
        assert "infozoom" in connectors

    def test_get_connector_returns_instance(self):
        connector = get_connector("json")
        assert isinstance(connector, JSONExportConnector)

    def test_get_connector_unknown_raises(self):
        with pytest.raises(KeyError):
            get_connector("does_not_exist")

    def test_list_connectors_returns_metadata(self):
        listing = list_connectors()
        assert isinstance(listing, list)
        names = [c["name"] for c in listing]
        assert "json" in names
        assert "mssql" in names
        assert "infozoom" in names
        for item in listing:
            assert "displayName" in item
            assert "fileExtension" in item


# ---------------------------------------------------------------------------
# JSON Connector
# ---------------------------------------------------------------------------

class TestJSONConnector:
    def setup_method(self):
        self.connector = JSONExportConnector()

    def test_validate_always_empty(self, minimal_model):
        assert self.connector.validate(minimal_model) == []

    def test_export_produces_valid_json(self, minimal_model):
        result = self.connector.export(minimal_model)
        data = json.loads(result)  # must not raise
        assert isinstance(data, dict)

    def test_export_schema_fields(self, minimal_model):
        data = json.loads(self.connector.export(minimal_model))
        assert data["version"] == "1.0"
        assert data["format"] == "nemo-rules-json"
        assert "generatedAt" in data
        assert "report" in data
        assert "summary" in data
        assert "groups" in data

    def test_export_report_info(self, minimal_model):
        data = json.loads(self.connector.export(minimal_model))
        assert data["report"]["id"] == "TEST_REPORT"
        assert data["report"]["displayName"] == "Test Report"

    def test_export_groups_and_rules(self, minimal_model):
        data = json.loads(self.connector.export(minimal_model))
        groups = data["groups"]
        assert len(groups) == 2
        first_group = groups[0]
        assert "rules" in first_group
        rules = first_group["rules"]
        assert len(rules) == 2
        # Check rule fields
        rule = rules[0]
        assert "active" in rule
        assert "condition" in rule
        assert "message" in rule
        assert "dimension" in rule

    def test_export_summary_counts(self, minimal_model):
        data = json.loads(self.connector.export(minimal_model))
        summary = data["summary"]
        assert summary["totalGroups"] == 2
        assert summary["totalRules"] == 4
        assert summary["activeRules"] == 3
        assert summary["inactiveRules"] == 1

    def test_export_with_indent_option(self, minimal_model):
        result = self.connector.export(minimal_model, options={"indent": 4})
        # 4-space indent means first-level keys have 4 spaces
        assert "    " in result

    def test_export_empty_model(self):
        result = self.connector.export({})
        data = json.loads(result)
        assert data["summary"]["totalGroups"] == 0
        assert data["groups"] == []


# ---------------------------------------------------------------------------
# MSSQL Connector
# ---------------------------------------------------------------------------

class TestMSSQLConnector:
    def setup_method(self):
        self.connector = MSSQLExportConnector()

    def test_validate_clean_model(self, minimal_model):
        warnings = self.connector.validate(minimal_model)
        # minimal_model has no NEMO-specific syntax → no warnings
        assert isinstance(warnings, list)

    def test_validate_nemo_syntax_produces_warnings(self, model_with_nemo_syntax):
        warnings = self.connector.validate(model_with_nemo_syntax)
        assert any("LIKE_REGEXPR" in w or "PATINDEX" in w for w in warnings)

    def test_export_contains_case_when(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "CASE" in result
        assert "WHEN" in result
        assert "END" in result

    def test_export_contains_cte(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "WITH checks AS" in result

    def test_export_mode_create_and_insert(self, minimal_model):
        result = self.connector.export(minimal_model, options={"mode": "create_and_insert"})
        assert "CREATE TABLE" in result
        assert "INSERT INTO" in result

    def test_export_mode_insert_only(self, minimal_model):
        result = self.connector.export(minimal_model, options={"mode": "insert_only"})
        assert "CREATE TABLE" not in result
        assert "INSERT INTO" in result

    def test_export_default_mode_is_create_and_insert(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "CREATE TABLE" in result

    def test_export_contains_header(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "NEMO DQM Report" in result
        assert "T-SQL" in result

    def test_export_warnings_embedded(self, model_with_nemo_syntax):
        result = self.connector.export(model_with_nemo_syntax)
        assert "WARNING" in result or "PATINDEX" in result

    def test_export_inactive_rules_skipped_in_case(self, minimal_model):
        result = self.connector.export(minimal_model)
        # Inactive rule message should not appear in the T-SQL output (no active THEN for it)
        assert "Kundennummer hat Leerzeichen" not in result

    def test_export_length_translated(self, model_with_nemo_syntax):
        result = self.connector.export(model_with_nemo_syntax)
        # LENGTH should be translated to LEN
        assert "LEN(" in result
        # No raw LENGTH( should remain (case-insensitive check)
        import re
        assert not re.search(r"\bLENGTH\s*\(", result, re.IGNORECASE)

    def test_export_no_crash_with_1000_rules(self, minimal_model):
        """Stress test: connector must handle large rule sets."""
        big_group = {
            "id": "group_big",
            "number": 3,
            "title": "Big Group",
            "displayName": "BigField",
            "internalName": "BIG_FIELD",
            "field": "BIG_FIELD",
            "description": "",
            "typeHints": [],
            "rules": [
                {
                    "id": f"rule_{i:05d}",
                    "number": i,
                    "active": True,
                    "dimension": "Korrektheit",
                    "ruleType": "custom",
                    "message": f"Error {i}",
                    "condition": f"BIG_FIELD = '{i}'",
                }
                for i in range(1000)
            ],
        }
        model = dict(minimal_model)
        model["checks"]["groups"] = [big_group]
        result = self.connector.export(model)
        assert "CASE" in result
        assert len(result) > 1000

    def test_get_options_schema(self):
        schema = self.connector.get_options_schema()
        assert "mode" in schema
        assert "create_and_insert" in schema["mode"]["options"]
        assert "insert_only" in schema["mode"]["options"]


# ---------------------------------------------------------------------------
# InfoZoom Connector
# ---------------------------------------------------------------------------

class TestInfoZoomConnector:
    def setup_method(self):
        self.connector = InfoZoomExportConnector()

    def test_validate_warns_on_empty_groups(self):
        model = {"checks": {"groups": []}, "source": {"attributes": []}}
        warnings = self.connector.validate(model)
        assert any("group" in w.lower() or "attribute" in w.lower() for w in warnings)

    def test_validate_clean_model(self, minimal_model):
        warnings = self.connector.validate(minimal_model)
        assert isinstance(warnings, list)

    def test_export_contains_header(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "INFOZOOM STRUCTURE DEFINITION" in result
        assert "Test Report" in result

    def test_export_contains_base_attributes(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "ATTRIBUTE: CUSTOMER_ID" in result
        assert "ATTRIBUTE: EMAIL" in result
        assert "ATTRIBUTE: ZIP_CODE" in result

    def test_export_contains_derived_attributes(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "DERIVED_ATTRIBUTE: CUSTOMER_ID_Validation" in result
        assert "DERIVED_ATTRIBUTE: EMAIL_Validation" in result

    def test_export_inactive_rules_excluded_by_default(self, minimal_model):
        result = self.connector.export(minimal_model)
        # Inactive rule "Kundennummer hat Leerzeichen" should not appear
        assert "Kundennummer hat Leerzeichen" not in result

    def test_export_inactive_rules_included_when_option_set(self, minimal_model):
        result = self.connector.export(minimal_model, options={"include_inactive": True})
        assert "Kundennummer hat Leerzeichen" in result

    def test_export_readable_descriptions(self, minimal_model):
        result = self.connector.export(minimal_model)
        # Should contain human-readable rule descriptions
        assert "empty" in result.lower() or "is required" in result.lower() or "IF" in result

    def test_export_ends_with_end_marker(self, minimal_model):
        result = self.connector.export(minimal_model)
        assert "END OF DEFINITION" in result


# ---------------------------------------------------------------------------
# ConditionTranslator
# ---------------------------------------------------------------------------

class TestConditionTranslator:
    def setup_method(self):
        self.translator = ConditionTranslator()

    # -- to_mssql --

    def test_length_to_len(self):
        sql, warning = self.translator.to_mssql("LENGTH(FIELD_A) > 5")
        assert "LEN(" in sql
        assert "LENGTH(" not in sql
        assert warning is None

    def test_trim_expanded(self):
        sql, warning = self.translator.to_mssql("TRIM(FIELD_A) <> FIELD_A")
        assert "LTRIM(RTRIM(" in sql
        assert warning is None

    def test_to_nvarchar_translated(self):
        sql, warning = self.translator.to_mssql("TO_NVARCHAR(FIELD_A) = ''")
        assert "CAST(" in sql
        assert "NVARCHAR(MAX)" in sql
        assert warning is None

    def test_like_regexpr_translated_with_warning(self):
        sql, warning = self.translator.to_mssql("FIELD_A LIKE_REGEXPR('^[0-9]+$')")
        assert "PATINDEX" in sql
        assert warning is not None
        assert "PATINDEX" in warning or "LIKE_REGEXPR" in warning

    def test_not_like_regexpr(self):
        sql, warning = self.translator.to_mssql("FIELD_A NOT LIKE_REGEXPR('^[0-9]+$')")
        assert "PATINDEX" in sql
        assert warning is not None

    def test_replace_regexpr_produces_warning(self):
        sql, warning = self.translator.to_mssql("REPLACE_REGEXPR('x' IN FIELD_A WITH 'y') = ''")
        assert warning is not None
        assert "REPLACE_REGEXPR" in warning

    def test_plain_condition_unchanged(self):
        cond = "FIELD_A IS NULL"
        sql, warning = self.translator.to_mssql(cond)
        assert sql == cond
        assert warning is None

    def test_like_unchanged(self):
        cond = "FIELD_A LIKE '%@%.%'"
        sql, warning = self.translator.to_mssql(cond)
        assert sql == cond
        assert warning is None

    # -- to_description_en --

    def test_is_null_description(self):
        desc = self.translator.to_description_en("FIELD_A IS NULL", "FIELD_A")
        assert "empty" in desc.lower() or "required" in desc.lower()

    def test_empty_string_description(self):
        desc = self.translator.to_description_en("FIELD_A = ''", "FIELD_A")
        assert "empty" in desc.lower() or "required" in desc.lower()

    def test_trim_description(self):
        desc = self.translator.to_description_en("TRIM(FIELD_A) <> FIELD_A", "FIELD_A")
        assert "whitespace" in desc.lower() or "trim" in desc.lower()

    def test_length_lt_description(self):
        desc = self.translator.to_description_en("LENGTH(FIELD_A) < 5", "FIELD_A")
        assert "shorter" in desc.lower() or "5" in desc

    def test_length_gt_description(self):
        desc = self.translator.to_description_en("LENGTH(FIELD_A) > 20", "FIELD_A")
        assert "longer" in desc.lower() or "20" in desc

    def test_like_regexpr_not_description(self):
        desc = self.translator.to_description_en("FIELD_A NOT LIKE_REGEXPR('^[0-9]+$')", "FIELD_A")
        assert "pattern" in desc.lower()

    def test_field_label_screaming_snake(self):
        label = ConditionTranslator._field_label("CUSTOMER_ID")
        assert label == "Customer Id"

    def test_field_label_empty(self):
        label = ConditionTranslator._field_label("")
        assert label == "Field"


# ---------------------------------------------------------------------------
# FieldCascader
# ---------------------------------------------------------------------------

class TestFieldCascader:
    def setup_method(self):
        self.cascader = FieldCascader()
        self.rules = [
            {
                "active": True,
                "condition": "FIELD_A IS NULL",
                "message": "Field A is required",
                "dimension": "Vollständigkeit",
            },
            {
                "active": True,
                "condition": "LENGTH(FIELD_A) > 20",
                "message": "Field A too long",
                "dimension": "Korrektheit",
            },
            {
                "active": False,
                "condition": "FIELD_A = 'TEST'",
                "message": "Test value found",
                "dimension": "Aktualität",
            },
        ]

    def test_mssql_cascade_contains_case(self):
        sql, warnings = self.cascader.build_cascade_mssql("FIELD_A", self.rules)
        assert "CASE" in sql
        assert "WHEN" in sql
        assert "END" in sql

    def test_mssql_cascade_skips_inactive(self):
        sql, warnings = self.cascader.build_cascade_mssql("FIELD_A", self.rules)
        # Inactive rule message should not appear
        assert "Test value found" not in sql

    def test_mssql_cascade_translates_length(self):
        sql, warnings = self.cascader.build_cascade_mssql("FIELD_A", self.rules)
        assert "LEN(" in sql

    def test_mssql_cascade_no_active_rules(self):
        inactive_only = [dict(r, active=False) for r in self.rules]
        sql, warnings = self.cascader.build_cascade_mssql("FIELD_A", inactive_only)
        # With no active rules the cascader still produces a valid CASE ELSE END block
        assert "CASE" in sql
        assert "ELSE" in sql
        assert "END" in sql
        assert "WHEN" not in sql  # no active rules means no WHEN clauses

    def test_infozoom_cascade_readable(self):
        text, warnings = self.cascader.build_cascade_infozoom("FIELD_A", self.rules)
        assert "IF" in text
        assert "THEN" in text

    def test_infozoom_cascade_skips_inactive(self):
        text, warnings = self.cascader.build_cascade_infozoom("FIELD_A", self.rules)
        # Inactive rule should not appear
        assert "Test value found" not in text

    def test_infozoom_cascade_no_active_rules(self):
        inactive_only = [dict(r, active=False) for r in self.rules]
        text, warnings = self.cascader.build_cascade_infozoom("FIELD_A", inactive_only)
        assert "no active" in text.lower()

    def test_infozoom_cascade_order_note_for_multiple(self):
        text, warnings = self.cascader.build_cascade_infozoom("FIELD_A", self.rules)
        # Multiple active rules → ordering note
        assert "order" in text.lower()


# ---------------------------------------------------------------------------
# API endpoint integration tests
# ---------------------------------------------------------------------------

class TestExportAPIEndpoint:
    """
    Integration tests for the export endpoint functions.
    These call the endpoint functions directly (no httpx dependency needed).
    """

    @pytest.fixture()
    def sample_editor_model(self, minimal_model) -> Dict[str, Any]:
        return minimal_model

    def test_list_connectors_endpoint(self):
        from backend.main import get_export_connectors
        result = get_export_connectors()
        assert "connectors" in result
        names = [c["name"] for c in result["connectors"]]
        assert "json" in names
        assert "mssql" in names
        assert "infozoom" in names

    def test_export_json_format(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="json", options={})
        response = export_editor_model("TEST_REPORT", request)
        import json as json_mod
        data = json_mod.loads(response.body)
        assert data["format"] == "nemo-rules-json"

    def test_export_mssql_format(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="mssql", options={})
        response = export_editor_model("TEST_REPORT", request)
        content = response.body.decode("utf-8")
        assert "CASE" in content or "CREATE TABLE" in content

    def test_export_infozoom_format(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="infozoom", options={})
        response = export_editor_model("TEST_REPORT", request)
        content = response.body.decode("utf-8")
        assert "INFOZOOM" in content

    def test_export_unknown_format_returns_400(self, sample_editor_model):
        from fastapi import HTTPException
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="unknown_xyz", options={})
        with pytest.raises(HTTPException) as exc_info:
            export_editor_model("TEST_REPORT", request)
        assert exc_info.value.status_code == 400

    def test_export_filename_in_disposition(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="mssql", options={})
        response = export_editor_model("TEST_REPORT", request)
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert ".sql" in disposition

    def test_export_warnings_header_present(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="mssql", options={})
        response = export_editor_model("TEST_REPORT", request)
        assert "x-export-warnings" in {k.lower() for k in response.headers.keys()}

    def test_export_mssql_insert_only_option(self, sample_editor_model):
        from backend.main import export_editor_model, EditorExportRequest
        request = EditorExportRequest(editorModel=sample_editor_model, format="mssql", options={"mode": "insert_only"})
        response = export_editor_model("TEST_REPORT", request)
        content = response.body.decode("utf-8")
        assert "CREATE TABLE" not in content
        assert "INSERT INTO" in content
