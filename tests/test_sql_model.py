import unittest
from pathlib import Path

from backend.services.sql_model import get_rule_catalog, merge_missing_group_metadata, normalize_editor_model, parse_editor_model, parse_group_header

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SqlModelTest(unittest.TestCase):
    def test_customer_structure_extracts_groups_rules_and_dimensions(self) -> None:
        sql = (PROJECT_ROOT / "structure_customer.sql").read_text(encoding="utf-8-sig")

        model = parse_editor_model(sql, {"displayName": "Kunden"})

        self.assertGreaterEqual(model["summary"]["checkGroupCount"], 20)
        self.assertGreater(model["summary"]["ruleCount"], 100)
        self.assertIn("Vollständigkeit", model["summary"]["dimensionCounts"])
        self.assertIn("Korrektheit", model["summary"]["dimensionCounts"])
        self.assertIn("Einheitlichkeit", model["summary"]["dimensionCounts"])
        self.assertIn("Aktualität", model["summary"]["dimensionCounts"])
        self.assertTrue(model["source"]["attributes"])
        self.assertEqual("CUSTOMER", model["source"]["masterDataSubType"])
        self.assertEqual([], model["source"]["exceptions"])
        self.assertTrue(model["output"]["fields"])
        first_group = model["checks"]["groups"][0]
        self.assertEqual("Kundenname", first_group["displayName"])
        self.assertEqual("ADDRESS_NAME1-3", first_group["field"])
        self.assertIn("Validiert", first_group["description"])

    def test_inactive_commented_rule_is_preserved(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT NAME1 FROM DUMMY
),
checks AS (
    SELECT j.*,
        (
            -- PRÜFUNG 1: NAME1
            -- NAME1 (S_Adresse.Name1)
            -- Beispiel | Typen: Korrektheit
            CASE
                -- Korrektheit
                WHEN NAME1 LIKE_REGEXPR 'x'
                    THEN '' --'|Name enthaelt x'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM customer_source j
)
SELECT
    DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION
FROM checks
"""

        model = parse_editor_model(sql)
        rule = model["checks"]["groups"][0]["rules"][0]

        self.assertFalse(rule["active"])
        self.assertEqual("Name enthaelt x", rule["message"])
        self.assertEqual("Korrektheit", rule["dimension"])

    def test_english_check_group_header_extracts_field_and_description(self) -> None:
        header = """
        -- CHECK GROUP 1: STREET VALIDATION (ADDRESS_STREET)
        -- Validates street field
"""
        group = parse_group_header(header, 1)
        self.assertEqual("ADDRESS_STREET", group["field"])
        self.assertEqual("Validates street field", group["description"])

    def test_missing_draft_group_names_are_merged_from_original(self) -> None:
        draft = {"checks": {"groups": [{"title": "Prüfung 1", "displayName": "Prüfung 1", "field": "", "description": "Bearbeitet"}]}}
        original = {"checks": {"groups": [{"title": "STREET VALIDATION", "displayName": "STREET VALIDATION", "internalName": "ADDRESS_STREET", "field": "ADDRESS_STREET"}]}}
        merged = merge_missing_group_metadata(draft, original)
        group = merged["checks"]["groups"][0]
        self.assertEqual("ADDRESS_STREET", group["field"])
        self.assertEqual("Bearbeitet", group["description"])

    def test_structure_file_with_when_when_creates_validation_warning(self) -> None:
        sql = (PROJECT_ROOT / "STRUCTURE.sql").read_text(encoding="utf-8-sig")

        model = parse_editor_model(sql)
        codes = {finding["code"] for finding in model["validation"]["findings"]}

        self.assertIn("duplicated_when", codes)

    def test_source_settings_extract_subtype_and_not_in_exception(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT CUSTOMER_I_D, MASTER_DATA_SUB_TYPE
    FROM $schema.$table
    WHERE UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
      AND CUSTOMER_I_D NOT IN ('100', '200')
),
checks AS (
    SELECT c.*, '' AS DEFICIENCY_DESCRIPTION FROM customer_source c
)
SELECT DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION FROM checks
"""

        source = parse_editor_model(sql)["source"]

        self.assertEqual("CUSTOMER", source["masterDataSubType"])
        self.assertEqual(
            [{"field": "CUSTOMER_I_D", "operator": "NOT IN", "values": ["100", "200"]}],
            source["exceptions"],
        )

    def test_rule_catalog_contains_dimensions_and_rule_types(self) -> None:
        catalog = get_rule_catalog()

        self.assertEqual(
            [
                "Vollständigkeit",
                "Validität",
                "Korrektheit",
                "Eindeutigkeit",
                "Konsistenz",
                "Aktualität",
                "Genauigkeit",
                "Redundanz",
                "Einheitlichkeit",
                "Relevanz",
                "Zuverlässigkeit",
                "Verständlichkeit",
            ],
            catalog["dimensions"],
        )
        self.assertIn("completeness", {item["id"] for item in catalog["ruleTypes"]})

    def test_normalize_editor_model_validates_edited_rules(self) -> None:
        model = {
            "blocks": [],
            "source": {"attributes": []},
            "output": {"fields": []},
            "checks": {
                "groups": [
                    {
                        "id": "group_001",
                        "rules": [
                            {
                                "id": "rule_001",
                                "active": True,
                                "dimension": "Korrektheit",
                                "ruleType": "regex",
                                "condition": "NAME1 LIKE_REGEXPR 'x'",
                                "message": "Name fehlerhaft",
                            }
                        ],
                    }
                ]
            },
        }

        normalized = normalize_editor_model(model)
        codes = {finding["code"] for finding in normalized["validation"]["findings"]}

        self.assertEqual(1, normalized["summary"]["activeRuleCount"])
        self.assertEqual("Name fehlerhaft", normalized["checks"]["groups"][0]["rules"][0]["message"])
        self.assertNotIn("message_without_pipe", codes)

    def test_normalize_editor_model_accepts_new_dq_dimensions(self) -> None:
        model = {
            "checks": {
                "groups": [
                    {
                        "id": "group_001",
                        "rules": [
                            {
                                "id": "rule_001",
                                "active": True,
                                "dimension": "Validität",
                                "ruleType": "custom",
                                "condition": "ADDRESS_CITY IS NOT NULL",
                                "message": "Ort ist nicht gültig",
                            }
                        ],
                    }
                ]
            }
        }

        normalized = normalize_editor_model(model)
        codes = {finding["code"] for finding in normalized["validation"]["findings"]}

        self.assertEqual("Validität", normalized["checks"]["groups"][0]["rules"][0]["dimension"])
        self.assertNotIn("unknown_dimension", codes)

    def test_normalize_editor_model_preserves_editable_group_metadata(self) -> None:
        model = {
            "checks": {
                "groups": [
                    {
                        "title": "Technischer Titel",
                        "displayName": "Freier Anzeigename",
                        "internalName": "ADDRESS_CITY",
                        "field": "ADDRESS_CITY",
                        "description": "Frei bearbeitbare Beschreibung",
                        "rules": [],
                    }
                ]
            }
        }

        group = normalize_editor_model(model)["checks"]["groups"][0]

        self.assertEqual("Freier Anzeigename", group["displayName"])
        self.assertEqual("ADDRESS_CITY", group["internalName"])
        self.assertEqual("ADDRESS_CITY", group["field"])
        self.assertEqual("Frei bearbeitbare Beschreibung", group["description"])


if __name__ == "__main__":
    unittest.main()
