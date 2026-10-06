import unittest
from pathlib import Path

from backend.services.report_utils import (
    filter_deficiency_reports,
    filter_primary_deficiency_reports,
    is_top_25_report,
    normalize_filename,
    select_reports,
    unique_report_paths,
)


class ReportUtilsTest(unittest.TestCase):
    def test_select_reports_exact_by_display_internal_or_id(self) -> None:
        reports = [
            {"displayName": "Alpha", "internalName": "alpha_internal", "id": "1"},
            {"displayName": "Beta", "internalName": "beta_internal", "id": "2"},
        ]

        selected = select_reports(reports, ["beta_internal"], [])

        self.assertEqual(["Beta"], [report["displayName"] for report in selected])

    def test_select_reports_contains_display_or_internal_name(self) -> None:
        reports = [
            {"displayName": "(DEFICIENCIES) Customers TOP 25", "internalName": "customers_top"},
            {"displayName": "Other", "internalName": "other"},
        ]

        selected = select_reports(reports, [], ["customers"])

        self.assertEqual(1, len(selected))
        self.assertEqual("customers_top", selected[0]["internalName"])

    def test_filter_deficiency_reports_uses_prefix(self) -> None:
        reports = [
            {"displayName": "(DEFICIENCIES) Customers", "internalName": "customers"},
            {"displayName": "Customers (DEFICIENCIES)", "internalName": "wrong_position"},
            {"displayName": "", "internalName": "(DEFICIENCIES) Suppliers"},
        ]

        selected = filter_deficiency_reports(reports)

        self.assertEqual(["customers", "(DEFICIENCIES) Suppliers"], [report["internalName"] for report in selected])

    def test_top_25_reports_are_recognized_by_display_or_internal_name(self) -> None:
        self.assertTrue(is_top_25_report({"displayName": "(DEFICIENCIES) Customers TOP 25"}))
        self.assertTrue(is_top_25_report({"internalName": "deficiencies_customers_top_25"}))
        self.assertFalse(is_top_25_report({"displayName": "(DEFICIENCIES) Customers TOP 250"}))
        self.assertFalse(is_top_25_report({"displayName": "(DEFICIENCIES) Customers"}))

    def test_primary_deficiency_reports_exclude_top_25(self) -> None:
        reports = [
            {"displayName": "(DEFICIENCIES) Customers", "internalName": "customers"},
            {"displayName": "(DEFICIENCIES) Customers TOP 25", "internalName": "customers_top_25"},
            {"displayName": "Customers", "internalName": "other"},
        ]

        selected = filter_primary_deficiency_reports(reports)

        self.assertEqual(["customers"], [report["internalName"] for report in selected])

    def test_normalize_filename_and_unique_paths(self) -> None:
        reports = [
            {"displayName": "(DEFICIENCIES) Aedress/Pruefung"},
            {"displayName": "(DEFICIENCIES) Aedress/Pruefung"},
        ]

        self.assertEqual("Ae_Oe_Ue_ss", normalize_filename("Ae/Oe/Ue/ss", "fallback"))
        paths = unique_report_paths(reports, Path("reports"), ".sql")

        self.assertEqual("001_(DEFICIENCIES) Aedress_Pruefung.sql", paths[0].name)
        self.assertEqual("002_(DEFICIENCIES) Aedress_Pruefung_2.sql", paths[1].name)


if __name__ == "__main__":
    unittest.main()
