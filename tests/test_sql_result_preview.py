import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd
from fastapi import HTTPException

from backend.main import (
    NemoReportWriteRequest,
    SqlResultPreviewRequest,
    _sql_fingerprint,
    _render_sql_payload,
    preview_generated_report_result,
    write_report_to_nemo,
)
from backend.services.nemo_client import load_temporary_sql_dataframe, _load_preview_report_dataframe
from backend.services.report_service import sql_result_preview


class SqlResultPreviewTest(unittest.TestCase):
    def test_edited_sql_is_used_instead_of_regenerating_model(self):
        source_sql = "SELECT 1 AS RULEDESCRIPTION FROM DUMMY"
        edited_sql = "SELECT 2 AS RULEDESCRIPTION FROM DUMMY"
        request = SqlResultPreviewRequest(
            configId="config-1", editorModel={}, sql=edited_sql,
            baseSqlHash=_sql_fingerprint(source_sql), expectedSqlHash=_sql_fingerprint(edited_sql),
        )
        with (
            patch("backend.main._load_reports", return_value=(SimpleNamespace(id="config-1"), [{
                "id": "report-1", "internalName": "report", "querySyntax": source_sql,
            }])),
            patch("backend.main._effective_pa_export_filter", return_value=None),
            patch("backend.main.render_sql_from_model") as regenerate,
        ):
            result = _render_sql_payload("report-1", request)
        self.assertEqual(edited_sql, result["sql"])
        regenerate.assert_not_called()

    def test_strict_download_preserves_identifiers(self):
        nemo = Mock()
        nemo.config.get_config_nemo_url.return_value = "https://nemo.example"
        response = Mock(status_code=200)
        response.json.return_value = "https://nemo.example/result.csv"
        download = Mock(content=b'IDENTIFIER,RULEDESCRIPTION,_RECORD_COUNT\n00123,|Name fehlt,1\n')
        with (
            patch("backend.services.nemo_client.getProjectID", return_value="project-1"),
            patch("backend.services.nemo_client.requests.post", return_value=response),
            patch("backend.services.nemo_client.requests.get", return_value=download),
        ):
            result = _load_preview_report_dataframe(nemo, "Master Data", "preview-id")
        self.assertEqual("00123", result.iloc[0]["IDENTIFIER"])
        self.assertNotIn("_RECORD_COUNT", result.columns)

    def test_strict_download_does_not_hide_parse_errors(self):
        nemo = Mock()
        nemo.config.get_config_nemo_url.return_value = "https://nemo.example"
        response = Mock(status_code=200)
        response.json.return_value = "https://nemo.example/result.csv"
        with (
            patch("backend.services.nemo_client.getProjectID", return_value="project-1"),
            patch("backend.services.nemo_client.requests.post", return_value=response),
            patch("backend.services.nemo_client.requests.get", return_value=Mock(content=b"")),
        ):
            with self.assertRaises(pd.errors.EmptyDataError):
                _load_preview_report_dataframe(nemo, "Master Data", "preview-id")

    def test_error_frequencies_cover_all_rows_and_count_each_error_once_per_record(self):
        df = pd.DataFrame({"RULEDESCRIPTION": ["|Name fehlt|PLZ ungültig", "|Name fehlt|Name fehlt", "", None, "|PLZ ungültig"]})
        result = sql_result_preview(df, max_rows=2)
        self.assertEqual(5, result["rowCount"])
        self.assertEqual(2, result["returnedRows"])
        self.assertEqual(3, result["recordsWithErrors"])
        self.assertEqual(4, result["errorOccurrences"])
        self.assertEqual([
            {"message": "Name fehlt", "count": 2, "percent": 40.0},
            {"message": "PLZ ungültig", "count": 2, "percent": 40.0},
        ], result["errorSummary"])

    def test_missing_error_column_is_distinct_from_no_errors(self):
        result = sql_result_preview(pd.DataFrame({"A": [1, 2]}))
        self.assertIsNone(result["recordsWithErrors"])
        self.assertIsNone(result["errorColumn"])
        self.assertEqual([], result["errorSummary"])

    def test_empty_result_keeps_attribute_count(self):
        result = sql_result_preview(pd.DataFrame(columns=["A", "B"]))
        self.assertEqual(0, result["rowCount"])
        self.assertEqual(2, result["attributeCount"])
        self.assertEqual([], result["rows"])
        self.assertEqual([], result["errorSummary"])

    def test_missing_result_is_not_reported_as_zero_rows(self):
        with self.assertRaises(ValueError):
            sql_result_preview(None)

    def test_temporary_report_runs_exact_sql_and_is_deleted(self):
        nemo = Mock()
        sql = "WITH checks AS (SELECT 1 FROM DUMMY) SELECT * FROM checks"
        nemo.LoadReport.return_value = pd.DataFrame({"A": [1]})

        def created_report(**_kwargs):
            report = nemo.createReports.call_args.kwargs["reports"][0]
            return [{"id": "temporary-id", "internalName": report.internalName}]

        with patch("backend.services.nemo_client.get_reports", side_effect=created_report):
            result = load_temporary_sql_dataframe(nemo, "Master Data", sql)
        self.assertEqual(sql, nemo.createReports.call_args.kwargs["reports"][0].querySyntax)
        nemo.LoadReport.assert_called_once_with(projectname="Master Data", report_guid="temporary-id")
        nemo.deleteReports.assert_called_once_with(reports=["temporary-id"])
        self.assertEqual(1, len(result))

    def test_cleanup_failure_is_visible(self):
        nemo = Mock()
        nemo.deleteReports.side_effect = RuntimeError("delete failed")

        def created_report(**_kwargs):
            report = nemo.createReports.call_args.kwargs["reports"][0]
            return [{"id": "temporary-id", "internalName": report.internalName}]

        with patch("backend.services.nemo_client.get_reports", side_effect=created_report):
            with self.assertRaisesRegex(RuntimeError, "konnte nicht gelöscht"):
                load_temporary_sql_dataframe(nemo, "Master Data", "SELECT 1 FROM DUMMY")

    def request(self, sql):
        return SqlResultPreviewRequest(
            configId="config-1", editorModel={},
            baseSqlHash=_sql_fingerprint("original"), expectedSqlHash=_sql_fingerprint(sql),
        )

    def test_stale_generated_sql_never_executes(self):
        with (
            patch("backend.main._render_sql_payload", return_value={"sql": "changed"}),
            patch("backend.main.load_temporary_sql_dataframe") as execute,
        ):
            with self.assertRaises(HTTPException) as raised:
                preview_generated_report_result("report-1", self.request("preview"))
        self.assertEqual(409, raised.exception.status_code)
        execute.assert_not_called()

    def test_invalid_generated_sql_never_executes(self):
        with (
            patch("backend.main._render_sql_payload", return_value={
                "sql": "preview", "validation": {"findings": [{"severity": "error"}]},
            }),
            patch("backend.main.load_temporary_sql_dataframe") as execute,
        ):
            with self.assertRaises(HTTPException) as raised:
                preview_generated_report_result("report-1", self.request("preview"))
        self.assertEqual(422, raised.exception.status_code)
        execute.assert_not_called()

    def test_writing_sql_different_from_displayed_preview_is_blocked(self):
        request = NemoReportWriteRequest(
            configId="config-1", editorModel={}, overwriteConfirmation="report-1",
            baseSqlHash=_sql_fingerprint("original"), expectedSqlHash=_sql_fingerprint("preview"),
        )
        with (
            patch("backend.main._render_sql_payload", return_value={"sql": "changed"}),
            patch("backend.main.update_reports_sql") as update,
        ):
            with self.assertRaises(HTTPException) as raised:
                write_report_to_nemo("report-1", request)
        self.assertEqual(409, raised.exception.status_code)
        update.assert_not_called()

    def test_endpoint_returns_counts_and_frequencies_without_updating_original(self):
        nemo = Mock()

        @contextmanager
        def context(_config_id):
            yield SimpleNamespace(id="config-1"), nemo

        with (
            patch("backend.main._render_sql_payload", return_value={"sql": "preview", "validation": {"findings": []}}),
            patch("backend.main._nemo_for_config", side_effect=context),
            patch("backend.main.load_temporary_sql_dataframe", return_value=pd.DataFrame({"A": [1, 1, 2]})) as execute,
            patch("backend.main.update_reports_sql") as update,
        ):
            result = preview_generated_report_result("report-1", self.request("preview"))
        execute.assert_called_once_with(nemo, "Master Data", "preview", strict=True)
        update.assert_not_called()
        self.assertEqual(3, result["preview"]["rowCount"])
        self.assertEqual(1, result["preview"]["attributeCount"])
