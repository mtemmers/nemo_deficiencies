import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend.services.report_export import (
    ReportExportError,
    export_reports,
    resolve_export_directory,
    tenant_export_directory,
)


class ReportExportTest(unittest.TestCase):
    def test_selected_reports_are_exported_with_index_and_metadata(self) -> None:
        reports = [
            {
                "id": "first-id",
                "displayName": "First report",
                "internalName": "first_report",
                "querySyntax": "SELECT 1 FROM DUMMY",
            },
            {
                "id": "second-id",
                "displayName": "Second report",
                "internalName": "second_report",
                "querySyntax": "SELECT 2 FROM DUMMY",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            result = export_reports(
                nemo=Mock(),
                project="Master Data",
                all_reports=reports,
                report_refs=["second_report"],
                contains_values=[],
                output_dir=Path(temp_dir),
                export_data=False,
                refresh_index=False,
            )

            sql_files = list((Path(temp_dir) / "sql").glob("*.sql"))
            self.assertEqual(1, result["selectedReportCount"])
            self.assertEqual(1, result["sqlFileCount"])
            self.assertEqual(1, len(sql_files))
            self.assertIn("SELECT 2", sql_files[0].read_text(encoding="utf-8-sig"))
            self.assertTrue((Path(temp_dir) / "reports_index.csv").exists())
            self.assertTrue((Path(temp_dir) / "reports_metadata.json").exists())

    def test_data_export_is_delegated_for_selected_reports(self) -> None:
        reports = [
            {
                "id": "first-id",
                "displayName": "First report",
                "internalName": "first_report",
                "querySyntax": "SELECT 1 FROM DUMMY",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "backend.services.report_export.export_report_data",
            return_value=({0: "data.csv"}, {0: (2, 1)}, {}),
        ) as export_data:
            result = export_reports(
                nemo=Mock(),
                project="Master Data",
                all_reports=reports,
                report_refs=[],
                contains_values=[],
                output_dir=Path(temp_dir),
                export_data=True,
                refresh_index=False,
            )

        export_data.assert_called_once()
        self.assertEqual(1, result["dataFileCount"])

    def test_empty_selection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, self.assertRaises(ReportExportError):
            export_reports(
                nemo=Mock(),
                project="Master Data",
                all_reports=[],
                report_refs=[],
                contains_values=[],
                output_dir=Path(temp_dir),
                export_data=False,
                refresh_index=False,
            )

    def test_environment_variables_are_expanded_in_output_path(self) -> None:
        with patch.dict("os.environ", {"NEMO_EXPORT_TEST": str(Path.home())}):
            path = resolve_export_directory("%NEMO_EXPORT_TEST%/exports")

        self.assertEqual((Path.home() / "exports").resolve(), path)

    def test_tenant_is_added_as_safe_export_subdirectory(self) -> None:
        base = Path("C:/exports")

        self.assertEqual(base / "nextgendemo", tenant_export_directory(base, "nextgendemo"))
        self.assertEqual(base / "Tenant_Name", tenant_export_directory(base, 'Tenant:/Name*'))
        self.assertEqual(base / "_CON", tenant_export_directory(base, "CON"))
        self.assertEqual(base / "tenant", tenant_export_directory(base, "  "))


if __name__ == "__main__":
    unittest.main()
