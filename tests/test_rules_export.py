"""Tests for rules export service (CSV generation)."""

import pytest
from backend.services.rules_export import (
    RuleStatusFilter,
    build_rules_csv,
    iter_rule_rows,
)


@pytest.fixture
def sample_report_models():
    """Sample report models for testing."""
    return [
        {
            "report": {
                "id": "REPORT_1",
                "internalName": "REPORT_1",
                "displayName": "Bericht 1",
            },
            "model": {
                "checks": {
                    "groups": [
                        {
                            "internalName": "FIELD_A",
                            "displayName": "Feld A",
                            "rules": [
                                {
                                    "active": True,
                                    "message": "Feld ist erforderlich",
                                    "dimension": "Vollständigkeit",
                                    "ruleType": "completeness",
                                    "condition": "FIELD_A IS NOT NULL",
                                },
                                {
                                    "active": False,
                                    "message": "Feld darf nicht leer sein",
                                    "dimension": "Validität",
                                    "ruleType": "trim_whitespace",
                                    "condition": "TRIM(FIELD_A) <> ''",
                                },
                            ],
                        },
                        {
                            "internalName": "FIELD_B",
                            "displayName": "Feld B",
                            "rules": [
                                {
                                    "active": True,
                                    "message": "Länge mindestens 3 Zeichen",
                                    "dimension": "Validität",
                                    "ruleType": "min_length",
                                    "condition": "LENGTH(FIELD_B) >= 3",
                                },
                            ],
                        },
                    ]
                }
            },
            "source": "nemo",
        },
        {
            "report": {
                "id": "REPORT_2",
                "internalName": "REPORT_2",
                "displayName": "Bericht 2 (Entwurf)",
            },
            "model": {
                "checks": {
                    "groups": [
                        {
                            "internalName": "FIELD_C",
                            "displayName": "Feld C",
                            "rules": [
                                {
                                    "active": True,
                                    "message": "Email-Format erforderlich",
                                    "dimension": "Validität",
                                    "ruleType": "regex",
                                    "condition": "FIELD_C LIKE '%@%.%'",
                                },
                            ],
                        },
                        {
                            "internalName": "FIELD_D",
                            "displayName": "Feld D",
                            "rules": [],
                        },
                    ]
                }
            },
            "source": "draft",
        },
    ]


def test_iter_rule_rows_all_rules(sample_report_models):
    """Test iteration over all rules."""
    rows = list(iter_rule_rows(sample_report_models, status_filter="both"))
    
    assert len(rows) == 5  # 2 + 2 + 1 (empty group)
    
    # Check first rule
    first_rule = rows[0]
    assert first_rule["report_name"] == "Bericht 1"
    assert first_rule["field_name"] == "Feld A"
    assert first_rule["rule_message"] == "Feld ist erforderlich"
    assert first_rule["rule_status"] == "Aktiv"
    assert first_rule["dq_type"] == "Vollständigkeit"
    assert first_rule["rule_type"] == "completeness"
    assert "FIELD_A" in first_rule["condition"]


def test_iter_rule_rows_active_only(sample_report_models):
    """Test filtering for active rules only."""
    rows = list(iter_rule_rows(sample_report_models, status_filter="active"))
    
    # Should have 3 active rules (excluding the inactive one)
    active_rules = [r for r in rows if r["rule_status"] == "Aktiv"]
    assert len(active_rules) >= 3
    
    # All should be marked as active
    for row in rows:
        if row["rule_message"] != "(keine Regeln)":
            assert row["rule_status"] == "Aktiv"


def test_iter_rule_rows_inactive_only(sample_report_models):
    """Test filtering for inactive rules only."""
    rows = list(iter_rule_rows(sample_report_models, status_filter="inactive"))
    
    # Should have at least 1 inactive rule
    assert len(rows) >= 1
    
    # All should be marked as inactive
    for row in rows:
        if row["rule_message"] != "(keine Regeln)":
            assert row["rule_status"] == "Inaktiv"


def test_iter_rule_rows_by_report(sample_report_models):
    """Test filtering by report ID."""
    rows = list(iter_rule_rows(sample_report_models, report_id_filter="REPORT_1"))
    
    # Should only have rules from REPORT_1
    for row in rows:
        assert row["report_id"] == "REPORT_1"


def test_iter_rule_rows_source_labels(sample_report_models):
    """Test correct source labeling in iter_rule_rows."""
    rows = list(iter_rule_rows(sample_report_models, status_filter="both"))
    
    # First report should be NEMO (source="nemo" -> "NEMO")
    report_1_rules = [r for r in rows if r["report_id"] == "REPORT_1"]
    for row in report_1_rules:
        assert row["source"] == "NEMO", f"Expected NEMO but got {row['source']}"
    
    # Second report should be Entwurf (source="draft" -> "Entwurf")
    report_2_rules = [r for r in rows if r["report_id"] == "REPORT_2"]
    for row in report_2_rules:
        assert row["source"] == "Entwurf", f"Expected Entwurf but got {row['source']}"


def test_build_rules_csv_de(sample_report_models):
    """Test CSV building in German."""
    csv_content = build_rules_csv(sample_report_models, language="de")
    
    # Check that CSV contains headers
    lines = csv_content.strip().split("\n")
    assert len(lines) > 1
    
    # First line should be headers (including BOM)
    header_line = lines[0]
    assert "Bericht" in header_line or "Report" in header_line
    assert "Regelgruppe" in header_line or "Rule" in header_line
    
    # Check content
    csv_text = "\n".join(lines)
    assert "Bericht 1" in csv_text
    assert "Feld A" in csv_text
    assert "Aktiv" in csv_text
    assert "Inaktiv" in csv_text


def test_build_rules_csv_en(sample_report_models):
    """Test CSV building in English."""
    csv_content = build_rules_csv(sample_report_models, language="en")
    
    lines = csv_content.strip().split("\n")
    assert len(lines) > 1
    
    # Check for English headers
    header_line = lines[0]
    assert "Report" in header_line
    
    # Check content contains German translated correctly
    csv_text = "\n".join(lines)
    assert "Report 1" in csv_text or "Bericht 1" in csv_text


def test_build_rules_csv_with_filter(sample_report_models):
    """Test CSV building with filters."""
    # Filter by report and status
    csv_content = build_rules_csv(
        sample_report_models,
        report_id_filter="REPORT_1",
        status_filter="active",
        language="de",
    )
    
    lines = csv_content.strip().split("\n")
    # Should have header + at least one data line
    assert len(lines) >= 2
    
    # All non-header lines should contain "Aktiv"
    for line in lines[1:]:
        if line.strip():
            assert "Aktiv" in line


def test_build_rules_csv_semicolon_delimiter(sample_report_models):
    """Test that CSV uses semicolon as delimiter."""
    csv_content = build_rules_csv(sample_report_models, language="de")
    
    lines = csv_content.strip().split("\n")
    header_line = lines[0]
    
    # Should have multiple columns separated by semicolon
    columns = header_line.split(";")
    assert len(columns) >= 8  # Minimum expected columns


def test_build_rules_csv_empty_groups(sample_report_models):
    """Test handling of groups with no rules."""
    csv_content = build_rules_csv(sample_report_models, language="de")
    
    # Should contain the "(keine Regeln)" marker
    assert "(keine Regeln)" in csv_content


def test_iter_rule_rows_condition_truncation(sample_report_models):
    """Test that long conditions are truncated."""
    # Add a rule with very long condition
    long_condition = "X" * 500
    sample_report_models[0]["model"]["checks"]["groups"][0]["rules"][0]["condition"] = long_condition
    
    rows = list(iter_rule_rows(sample_report_models))
    first_rule = rows[0]
    
    # Condition should be truncated to max 200 chars
    assert len(first_rule["condition"]) <= 200


def test_rules_export_with_draft_and_nemo(sample_report_models):
    """Test export correctly distinguishes draft and NEMO sources."""
    csv_content = build_rules_csv(sample_report_models, language="de")
    
    lines = csv_content.strip().split("\n")
    csv_text = "\n".join(lines)
    
    # Both sources should be represented
    assert "NEMO" in csv_text
    assert "Entwurf" in csv_text
