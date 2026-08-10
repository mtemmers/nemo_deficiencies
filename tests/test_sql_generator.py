import re
import unittest
from pathlib import Path

from backend.services.sql_generator import localize_dimension, render_sql_from_model, render_top_25_sql
from backend.services.sql_model import parse_editor_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SqlGeneratorTest(unittest.TestCase):
    def test_all_dq_dimensions_have_distinct_english_labels(self) -> None:
        expected = {
            "Vollständigkeit": "Completeness",
            "Validität": "Validity",
            "Korrektheit": "Correctness",
            "Eindeutigkeit": "Uniqueness",
            "Konsistenz": "Consistency",
            "Aktualität": "Timeliness",
            "Genauigkeit": "Accuracy",
            "Redundanz": "Redundancy",
            "Einheitlichkeit": "Uniformity",
            "Relevanz": "Relevance",
            "Zuverlässigkeit": "Reliability",
            "Verständlichkeit": "Understandability",
        }

        self.assertEqual(
            expected,
            {dimension: localize_dimension(dimension, "en") for dimension in expected},
        )

    def test_report_language_localizes_generated_sql_comments(self) -> None:
        sql = (PROJECT_ROOT / "structure_customer.sql").read_text(encoding="utf-8-sig")
        model = parse_editor_model(sql, {"displayName": "Customers"})
        model["reportLanguage"] = "en"

        result = render_sql_from_model(sql, model)

        self.assertIn("-- Generated at:", result.sql)
        self.assertIn("-- Check groups:", result.sql)
        self.assertIn("-- CHECK 1:", result.generated_checks_sql)
        self.assertIn("-- Completeness", result.generated_checks_sql)

    def test_adds_new_rule_group_field_to_source_projection(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT
        CUSTOMER_I_D,
        MASTER_DATA_SUB_TYPE -- letzter Wert mit Kommentar
    FROM $schema.$table
    WHERE UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
),
checks AS (
    SELECT c.*,
        (CASE WHEN CUSTOMER_I_D IS NULL THEN '|Fehlt' ELSE '' END) AS DEFICIENCY_DESCRIPTION
    FROM customer_source c
)
SELECT
    DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION,
    '' AS DESCRIPTION2
FROM checks
"""
        model = parse_editor_model(sql)
        model["source"]["attributes"].append({
            "name": "CUSTOMER_ASSOCIATION",
            "expression": "CUSTOMER_ASSOCIATION",
            "displayName": "Kundenzuordnung",
            "comment": "Kundenzuordnung",
        })

        first_render = render_sql_from_model(sql, model)
        second_render = render_sql_from_model(first_render.sql, model)

        self.assertIn("CUSTOMER_ASSOCIATION", first_render.sql)
        self.assertRegex(first_render.sql, r"CUSTOMER_ASSOCIATION\s*\n\s*FROM")
        self.assertIn("'|<Kundenzuordnung>' || COALESCE(TO_NVARCHAR(CUSTOMER_ASSOCIATION), '')", first_render.sql)
        self.assertEqual(1, second_render.sql.count("|<Kundenzuordnung>"))
        self.assertEqual(
            1,
            len(re.findall(r"(?m)^\s*CUSTOMER_ASSOCIATION\s*,?\s*$", second_render.sql)),
        )

    def test_adds_raw_field_when_it_only_occurs_in_a_computed_attribute(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT
        TRIM(CUSTOMER_ASSOCIATION) AS CLEAN_ASSOCIATION -- CUSTOMER_ASSOCIATION helper
    FROM $schema.$table
),
checks AS (
    SELECT c.*, '' AS DEFICIENCY_DESCRIPTION FROM customer_source c
)
SELECT DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION FROM checks
"""
        model = parse_editor_model(sql)
        model["source"]["attributes"].append({"name": "CUSTOMER_ASSOCIATION", "expression": "CUSTOMER_ASSOCIATION", "comment": ""})

        result = render_sql_from_model(sql, model)

        self.assertRegex(result.sql, r"(?m)^\s+CUSTOMER_ASSOCIATION\s*$")

    def test_render_source_subtype_and_exceptions(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT CUSTOMER_I_D, MASTER_DATA_SUB_TYPE
    FROM $schema.$table
    WHERE UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
      AND CUSTOMER_I_D NOT IN ('OLD')
),
checks AS (
    SELECT c.*,
        (CASE WHEN CUSTOMER_I_D IS NULL THEN '|Fehlt' ELSE '' END) AS DEFICIENCY_DESCRIPTION
    FROM customer_source c
)
SELECT DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION FROM checks
"""
        model = parse_editor_model(sql)
        model["source"]["masterDataSubType"] = "SUPPLIER"
        model["source"]["exceptions"] = [
            {"field": "CUSTOMER_I_D", "operator": "NOT IN", "values": ["100", "200"]}
        ]

        result = render_sql_from_model(sql, model)

        self.assertIn("UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'SUPPLIER'", result.sql)
        self.assertIn("CUSTOMER_I_D NOT IN ('100', '200')", result.sql)
        self.assertNotIn("NOT IN ('OLD')", result.sql)

    def test_render_top_25_sql_limits_and_sorts_final_select(self) -> None:
        sql = "WITH source AS (\n    SELECT 1 AS VALUE FROM DUMMY\n)\nSELECT\n    VALUE AS ERROREVALUATION\nFROM source;\n"

        result = render_top_25_sql(sql)

        self.assertIn("SELECT TOP 25\n    VALUE AS ERROREVALUATION", result)
        self.assertEqual(1, result.count("TOP 25"))
        self.assertTrue(result.rstrip().endswith("ORDER BY ERROREVALUATION DESC"))

    def test_render_top_25_sql_replaces_existing_limit_and_order(self) -> None:
        sql = "SELECT TOP 10 1 AS ERROREVALUATION FROM DUMMY\nORDER BY ERROREVALUATION ASC;"

        result = render_top_25_sql(sql)

        self.assertIn("SELECT TOP 25", result)
        self.assertNotIn("TOP 10", result)
        self.assertNotIn("ERROREVALUATION ASC", result)
        self.assertEqual(1, result.upper().count("ORDER BY"))
    def test_render_customer_checks_block_from_editor_model(self) -> None:
        sql = (PROJECT_ROOT / "structure_customer.sql").read_text(encoding="utf-8-sig")
        model = parse_editor_model(sql, {"displayName": "Kunden"})
        first_rule = model["checks"]["groups"][0]["rules"][0]
        first_rule["message"] = "SQL Generator Test"

        result = render_sql_from_model(sql, model)
        reparsed = parse_editor_model(result.sql, {"displayName": "Kunden"})

        self.assertTrue(result.changed)
        self.assertTrue(result.sql.startswith("-- ================================================================================"))
        self.assertIn("NEMO DQM Report SQL", result.sql)
        self.assertRegex(result.sql, r"-- Generated At: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")
        self.assertIn("-- Checks:", result.sql)
        self.assertIn("checks AS (", result.generated_checks_sql)
        self.assertIn("THEN '|SQL Generator Test'", result.generated_checks_sql)
        self.assertNotIn("WHEN WHEN", result.sql.upper())
        self.assertEqual(model["summary"]["checkGroupCount"], reparsed["summary"]["checkGroupCount"])

    def test_render_supplier_structure_removes_duplicated_when(self) -> None:
        sql = (PROJECT_ROOT / "STRUCTURE.sql").read_text(encoding="utf-8-sig")
        model = parse_editor_model(sql, {"displayName": "Lieferanten"})

        result = render_sql_from_model(sql, model)

        self.assertTrue(result.changed)
        self.assertIn("checks AS (", result.generated_checks_sql)
        self.assertNotIn("WHEN WHEN", result.sql.upper())
        self.assertEqual(1, result.sql.upper().count("SUPPLIER_I_D NOT IN"))

    def test_inactive_rule_is_rendered_as_commented_message(self) -> None:
        sql = """
WITH customer_source AS (
    SELECT NAME1 FROM DUMMY
),
checks AS (
    SELECT j.*,
        (
            -- PRÜFUNG 1: NAME1
            -- NAME1
            -- Beispiel | Typen: Korrektheit
            CASE
                -- Korrektheit
                WHEN NAME1 LIKE_REGEXPR 'x'
                    THEN '' --'|Name enthaelt x'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        customer_source j
)
SELECT
    DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION
FROM checks
"""
        model = parse_editor_model(sql)

        result = render_sql_from_model(sql, model)
        reparsed = parse_editor_model(result.sql)
        rule = reparsed["checks"]["groups"][0]["rules"][0]

        self.assertIn("THEN '' --'|Name enthaelt x'", result.generated_checks_sql)
        self.assertFalse(rule["active"])
        self.assertEqual("Name enthaelt x", rule["message"])


    def test_missing_dimension_is_inferred_for_sql_comment(self) -> None:
        sql = """
WITH source AS (
    SELECT NAME1 FROM DUMMY
),
checks AS (
    SELECT j.*,
        (
            CASE
                WHEN NAME1 IS NULL OR TRIM(NAME1) = ''
                    THEN '|Name fehlt'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        source j
)
SELECT
    DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION
FROM checks
"""
        model = parse_editor_model(sql)
        rule = model["checks"]["groups"][0]["rules"][0]
        rule["dimension"] = ""
        rule["message"] = "Name fehlt"

        result = render_sql_from_model(sql, model)

        self.assertIn("-- Vollständigkeit", result.generated_checks_sql)
        self.assertIn("THEN '|Name fehlt'", result.generated_checks_sql)
if __name__ == "__main__":
    unittest.main()
