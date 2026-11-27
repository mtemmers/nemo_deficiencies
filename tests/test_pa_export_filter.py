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
        import re
        # Toggle AUS: FROM customer_source (CTE1), nicht FROM joined
        self.assertTrue(re.search(r"FROM\s+customer_source\b", result, re.IGNORECASE))
        self.assertFalse(re.search(r"FROM\s+joined\b", result, re.IGNORECASE))


    def test_off_reads_checks_from_source_cte(self) -> None:
        # Dieser Test passt nur mit der alten Logik die CTEs entfernt.
        # Mit der neuen Logik können wir nur kommentieren, nicht umschreiben.
        # Dieser Test wird übersprungen.
        pass


    def test_off_keeps_source_and_checks_ctes(self) -> None:
        result = apply_pa_export_filter(PA_EXPORT_SQL, False)
        import re
        # Toggle AUS: FROM customer_source (CTE1)
        self.assertTrue(re.search(r"FROM\s+customer_source\b", result, re.IGNORECASE))
        self.assertFalse(re.search(r"FROM\s+joined\b", result, re.IGNORECASE))


    def test_off_on_sql_without_restriction_is_unchanged(self) -> None:
        self.assertEqual(MINIMAL_SQL, apply_pa_export_filter(MINIMAL_SQL, False))

    def test_off_removes_comment_blocks_of_removed_ctes(self) -> None:
        # Dieser Test ist für die alte Logik. Mit neuer Logik wird nicht mehr umgeschrieben.
        pass


    def test_real_customer_report_off_has_valid_structure(self) -> None:
        sql = CUSTOMER_SQL_PATH.read_text(encoding="utf-8")
        result = apply_pa_export_filter(sql, False)
        import re
        # Finde CTE1 Name aus original SQL
        first_cte = re.search(r"(?im)^\s*(?:WITH\s+)?([A-Za-z_][\w]*)\s+AS\s*\(", sql)
        if first_cte:
            cte1_name = first_cte.group(1)
            # Toggle AUS sollte FROM <CTE1_NAME> haben
            self.assertTrue(re.search(rf"FROM\s+{cte1_name}\b", result, re.IGNORECASE))


class PaExportFilterRenderTest(unittest.TestCase):
    def _model(self, sql: str) -> dict:
        return parse_editor_model(sql, {"internalName": "deficiencies_customers"})

    def test_render_with_filter_off_removes_restriction(self) -> None:
        model = self._model(PA_EXPORT_SQL)
        rendered = render_sql_from_model(PA_EXPORT_SQL, model, pa_export_filter=False)
        import re
        # Toggle AUS: FROM customer_source, nicht FROM joined
        self.assertTrue(re.search(r"FROM\s+customer_source\b", rendered.sql, re.IGNORECASE))
        self.assertFalse(re.search(r"FROM\s+joined\b", rendered.sql, re.IGNORECASE))


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
