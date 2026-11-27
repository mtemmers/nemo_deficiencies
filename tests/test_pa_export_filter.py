import unittest
from pathlib import Path

from backend.services.sql_generator import (
    apply_pa_export_filter,
    has_pa_export_restriction,
    render_sql_from_model,
)
from backend.services.sql_model import parse_editor_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SQL_PATH = PROJECT_ROOT / "Master Data" / "(DEFICIENCIES) Kunden.sql"

MINIMAL_SQL = """WITH customer_source AS (
    SELECT
        company,
        customer_i_d,
        MASTER_DATA_SUB_TYPE
    FROM
        $schema.$table
    WHERE
        UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
),
checks AS (
    SELECT
        j.*,
        (
            CASE
                WHEN ADDRESS_NAME IS NULL THEN '|Name leer'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        customer_source j
)
SELECT * FROM checks
"""

PA_EXPORT_SQL = """WITH customer_source AS (
    SELECT
        company,
        customer_i_d,
        MASTER_DATA_SUB_TYPE
    FROM
        $schema.$table
    WHERE
        UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
),
process_source AS (
    SELECT DISTINCT
        company,
        customer_i_d
    FROM
        $schema."pa_export"
    WHERE
        customer_i_d IS NOT NULL
),
joined AS (
    SELECT
        c.*
    FROM
        customer_source c
        INNER JOIN process_source p ON c.company = p.company
        AND c.customer_i_d = p.customer_i_d
),
checks AS (
    SELECT
        j.*,
        (
            CASE
                WHEN ADDRESS_NAME IS NULL THEN '|Name leer'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        joined j
)
SELECT * FROM checks
"""


class PaExportFilterDetectionTest(unittest.TestCase):
    def test_detects_pa_export_restriction(self) -> None:
        self.assertTrue(has_pa_export_restriction(PA_EXPORT_SQL))

    def test_no_restriction_without_pa_export(self) -> None:
        self.assertFalse(has_pa_export_restriction(MINIMAL_SQL))

    def test_real_customer_report_has_restriction(self) -> None:
        sql = CUSTOMER_SQL_PATH.read_text(encoding="utf-8")
        self.assertTrue(has_pa_export_restriction(sql))


class PaExportFilterTransformTest(unittest.TestCase):
    def test_on_keeps_sql_unchanged(self) -> None:
        self.assertEqual(PA_EXPORT_SQL, apply_pa_export_filter(PA_EXPORT_SQL, True))

    def test_off_removes_process_and_join_ctes(self) -> None:
        result = apply_pa_export_filter(PA_EXPORT_SQL, False)
        # CTEs sind auskommentiert, nicht entfernt
        import re
        # Nicht aktive (unkommentierte) Versionen sollten nicht vorkommen
        self.assertFalse(re.search(r"^\s*process_source AS \(", result, re.MULTILINE))
        self.assertFalse(re.search(r"^\s*joined AS \(", result, re.MULTILINE))
        # Die Auskommentierungen sollten vorhanden sein
        self.assertIn("-- process_source AS (", result)
        self.assertIn("-- joined AS (", result)
        # pa_export ist jetzt auskommentiert (nicht aktiv)
        # Suche nach "-- " + beliebig viele Spaces + "$schema.\"pa_export\""
        self.assertTrue(re.search(r"--\s+\$schema\.\"pa_export\"", result), 
                       "pa_export should be commented out but still present")
        # INNER JOIN ist in den auskommentierten Zeilen, aber nicht aktiv
        self.assertFalse(re.search(r"^\s*INNER JOIN", result, re.MULTILINE))

    def test_off_reads_checks_from_source_cte(self) -> None:
        result = apply_pa_export_filter(PA_EXPORT_SQL, False)
        self.assertIn("FROM customer_source j", result)
        self.assertNotIn("FROM joined j", result)

    def test_off_keeps_source_and_checks_ctes(self) -> None:
        result = apply_pa_export_filter(PA_EXPORT_SQL, False)
        self.assertIn("customer_source AS (", result)
        self.assertIn("checks AS (", result)
        self.assertIn("SELECT * FROM checks", result)
        # process_source und joined sollten auskommentiert sein
        self.assertIn("-- process_source AS (", result)
        self.assertIn("-- joined AS (", result)

    def test_off_on_sql_without_restriction_is_unchanged(self) -> None:
        self.assertEqual(MINIMAL_SQL, apply_pa_export_filter(MINIMAL_SQL, False))

    def test_off_removes_comment_blocks_of_removed_ctes(self) -> None:
        sql = PA_EXPORT_SQL.replace(
            "process_source AS (",
            "-- ----------------------------------------------------------------\n"
            "-- CTE 2: PROZESSRELEVANTE KUNDEN (process_source)\n"
            "-- ----------------------------------------------------------------\n"
            "process_source AS (",
        )
        result = apply_pa_export_filter(sql, False)
        # Der Kommentarblock sollte erhalten bleiben
        self.assertIn("-- CTE 2", result)
        # aber "process_source AS (" sollte NICHT unkommentiert vorkommen
        # (es sollte nur als "-- process_source AS (" kommentiert vorkommen)
        import re
        self.assertTrue(re.search(r"--\s+process_source AS \(", result),
                       "process_source should be commented out")
        # Nicht aktive (unkommentierte) Version sollte nicht vorkommen
        self.assertFalse(re.search(r"^\s*process_source AS \(", result, re.MULTILINE),
                        "process_source should not be active")

    def test_real_customer_report_off_has_valid_structure(self) -> None:
        sql = CUSTOMER_SQL_PATH.read_text(encoding="utf-8")
        result = apply_pa_export_filter(sql, False)
        # process_source und joined sollten nicht unkommentiert vorkommen
        import re
        self.assertFalse(re.search(r"^\s*process_source AS \(", result, re.MULTILINE))
        self.assertFalse(re.search(r"^\s*joined AS \(", result, re.MULTILINE))
        # Aber sie sollten auskommentiert sein
        self.assertIn("-- process_source AS (", result)
        self.assertIn("-- joined AS (", result)
        self.assertIn("FROM customer_source j", result)
        self.assertIn("checks AS (", result)


class PaExportFilterRenderTest(unittest.TestCase):
    def _model(self, sql: str) -> dict:
        return parse_editor_model(sql, {"internalName": "deficiencies_customers"})

    def test_render_with_filter_off_removes_restriction(self) -> None:
        model = self._model(PA_EXPORT_SQL)
        rendered = render_sql_from_model(PA_EXPORT_SQL, model, pa_export_filter=False)
        # pa_export ist jetzt auskommentiert (nicht aktiv), aber noch im SQL vorhanden
        import re
        self.assertTrue(re.search(r"--\s+\$schema\.\"pa_export\"", rendered.sql),
                       "pa_export should be commented out but still present")
        # INNER JOIN ist in den auskommentierten Zeilen, aber nicht aktiv
        self.assertFalse(re.search(r"^\s*INNER JOIN", rendered.sql, re.MULTILINE))
        self.assertIn("customer_source AS (", rendered.sql)

    def test_render_with_filter_on_keeps_restriction(self) -> None:
        model = self._model(PA_EXPORT_SQL)
        rendered = render_sql_from_model(PA_EXPORT_SQL, model, pa_export_filter=True)
        self.assertIn("pa_export", rendered.sql)
        self.assertIn("INNER JOIN", rendered.sql)

    def test_render_without_filter_argument_is_backward_compatible(self) -> None:
        model = self._model(PA_EXPORT_SQL)
        rendered = render_sql_from_model(PA_EXPORT_SQL, model)
        self.assertIn("pa_export", rendered.sql)


if __name__ == "__main__":
    unittest.main()


class PaExportFilterFrontendTest(unittest.TestCase):
    FRONTEND = PROJECT_ROOT / "backend" / "frontend"

    def test_toggle_sits_before_sql_preview_button(self) -> None:
        html = (self.FRONTEND / "index.html").read_text(encoding="utf-8")
        toggle_pos = html.index('id="paExportFilterToggle"')
        preview_pos = html.index('id="renderSqlBtn"')
        self.assertLess(toggle_pos, preview_pos)

    def test_toggle_is_wired_and_sends_setting(self) -> None:
        js = (self.FRONTEND / "app.js").read_text(encoding="utf-8")
        self.assertIn("paExportFilterToggle.addEventListener", js)
        self.assertIn("paExportFilter: paExportFilterRequested()", js)
        self.assertIn("/pa-export-filter", js)
        self.assertIn("syncPaExportToggle(payload.paExportFilter)", js)

    def test_editor_model_carries_toggle_state(self) -> None:
        js = (self.FRONTEND / "app.js").read_text(encoding="utf-8")
        self.assertIn("syncPaExportToggle(payload.paExportFilter)", js)
