import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd

from backend.services.nemo_client import (
    ReportTenantMismatchError,
    _create_customized_report,
    _updated_report,
    column_to_dict,
    get_columns,
    load_project_field_values,
    update_report_sql,
    update_reports_sql,
)


class NemoClientTest(unittest.TestCase):
    def test_field_profile_report_selects_one_column_and_is_deleted(self) -> None:
        nemo = Mock()
        nemo.LoadReport.return_value = pd.DataFrame({"FIELD_VALUE": ["A", "B"]})
        with patch(
            "backend.services.nemo_client.get_reports",
            return_value=[{"id": "temp-id", "internalName": "placeholder"}],
        ) as reports_mock:
            def reports_with_created_name(*_args, **_kwargs):
                report = nemo.createReports.call_args.kwargs["reports"][0]
                return [{"id": "temp-id", "internalName": report.internalName}]

            reports_mock.side_effect = reports_with_created_name
            values = load_project_field_values(nemo, "Master Data", "CUSTOMER_ID", 100)

        report = nemo.createReports.call_args.kwargs["reports"][0]
        self.assertEqual(["A", "B"], values)
        self.assertIn("TO_NVARCHAR(CUSTOMER_ID)", report.querySyntax)
        self.assertIn("FROM $schema.$table", report.querySyntax)
        self.assertNotIn("OTHER_FIELD", report.querySyntax)
        nemo.deleteReports.assert_called_once_with(reports=["temp-id"])

    def test_field_profile_report_is_deleted_when_download_fails(self) -> None:
        nemo = Mock()
        nemo.LoadReport.side_effect = RuntimeError("download failed")

        def created_report(*_args, **_kwargs):
            report = nemo.createReports.call_args.kwargs["reports"][0]
            return [{"id": "temp-id", "internalName": report.internalName}]

        with patch("backend.services.nemo_client.get_reports", side_effect=created_report):
            with self.assertRaises(RuntimeError):
                load_project_field_values(nemo, "Master Data", "CUSTOMER_ID", 100)

        nemo.deleteReports.assert_called_once_with(reports=["temp-id"])

    def test_field_profile_cleanup_retries_report_lookup(self) -> None:
        nemo = Mock()
        calls = 0

        def report_lookup(*_args, **_kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("temporary list error")
            report = nemo.createReports.call_args.kwargs["reports"][0]
            return [{"id": "temp-id", "internalName": report.internalName}]

        with patch("backend.services.nemo_client.get_reports", side_effect=report_lookup):
            with self.assertRaises(RuntimeError):
                load_project_field_values(nemo, "Master Data", "CUSTOMER_ID", 100)

        nemo.deleteReports.assert_called_once_with(reports=["temp-id"])

    def test_column_to_dict_keeps_search_relevant_fields(self) -> None:
        column = SimpleNamespace(
            id="col-1",
            displayName="Ort",
            internalName="ADDRESS_CITY",
            importName="address_city",
            description="Ort der Adresse",
            dataType="string",
            columnType="Imported",
            parentAttributeGroupInternalName="ADDRESS",
        )

        result = column_to_dict(column)

        self.assertEqual("Ort", result["displayName"])
        self.assertEqual("ADDRESS_CITY", result["internalName"])
        self.assertEqual("address_city", result["importName"])
        self.assertEqual("Ort der Adresse", result["description"])

    def test_get_columns_sorts_and_uses_project_name(self) -> None:
        fake_nemo = FakeNemo(
            [
                SimpleNamespace(displayName="Strasse", internalName="ADDRESS_STREET"),
                SimpleNamespace(displayName="Ort", internalName="ADDRESS_CITY"),
            ]
        )

        result = get_columns(fake_nemo, project="Master Data")

        self.assertEqual("Master Data", fake_nemo.projectname)
        self.assertEqual(["ADDRESS_CITY", "ADDRESS_STREET"], [column["internalName"] for column in result])

    def test_update_report_sql_preserves_metadata(self) -> None:
        fake_nemo = FakeNemo([])
        report = {
            "id": "report-1",
            "displayName": "(DEFICIENCIES) Customers",
            "internalName": "deficiencies_customers",
            "description": "Customers DQ",
            "columns": ["customer_id"],
            "reportCategories": ["DQM"],
            "isCustom": True,
        }

        update_report_sql(fake_nemo, "Master Data", report, "SELECT 1 FROM DUMMY")

        self.assertEqual("Master Data", fake_nemo.created_project)
        updated = fake_nemo.created_reports[0]
        self.assertEqual("deficiencies_customers", updated.internalName)
        self.assertEqual("SELECT 1 FROM DUMMY", updated.querySyntax)
        self.assertEqual(["CUSTOMER_ID"], updated.columns)
        self.assertEqual(["DQM"], updated.reportCategories)

    def test_update_reports_sql_sends_both_reports_in_one_call(self) -> None:
        fake_nemo = FakeNemo([])
        base = {
            "id": "report-1",
            "displayName": "(DEFICIENCIES) Customers",
            "internalName": "deficiencies_customers",
        }
        top = {
            "id": "report-2",
            "displayName": "(DEFICIENCIES) Customers TOP 25",
            "internalName": "deficiencies_customers_top_25",
        }

        update_reports_sql(fake_nemo, "Master Data", [(base, "SELECT 1"), (top, "SELECT TOP 25 1")])

        self.assertEqual(2, len(fake_nemo.created_reports))
        self.assertEqual(
            ["deficiencies_customers", "deficiencies_customers_top_25"],
            [report.internalName for report in fake_nemo.created_reports],
        )

    def test_standard_report_is_created_as_customized_report(self) -> None:
        fake_nemo = FakeNemo([])
        report = {
            "id": "standard-report",
            "displayName": "(DEFICIENCIES) Customers",
            "internalName": "deficiencies_customers",
            "isCustom": False,
        }

        with patch("backend.services.nemo_client._create_customized_report") as create_customized:
            update_reports_sql(fake_nemo, "Master Data", [(report, "SELECT 1")])

        create_customized.assert_called_once()
        self.assertFalse(hasattr(fake_nemo, "created_reports"))

    def test_custom_report_from_other_tenant_is_rejected_before_write(self) -> None:
        fake_nemo = FakeNemo([], tenant="gmt")
        report = {
            "id": "foreign-custom-report",
            "displayName": "(DEFICIENCIES) Parts",
            "internalName": "deficiencies_parts",
            "tenant": "wsm",
            "isCustom": True,
        }

        with (
            patch("backend.services.nemo_client._create_customized_report") as create_customized,
            self.assertRaises(ReportTenantMismatchError) as raised,
        ):
            update_reports_sql(fake_nemo, "Master Data", [(report, "SELECT 1")])

        self.assertIn("Tenant 'gmt'", str(raised.exception))
        self.assertIn("'wsm'", str(raised.exception))
        create_customized.assert_not_called()
        self.assertFalse(hasattr(fake_nemo, "created_reports"))

    def test_custom_report_from_current_tenant_is_updated(self) -> None:
        fake_nemo = FakeNemo([], tenant="gmt")
        report = {
            "id": "own-custom-report",
            "displayName": "(DEFICIENCIES) Parts",
            "internalName": "deficiencies_parts",
            "tenant": "GMT",
            "isCustom": True,
        }

        update_reports_sql(fake_nemo, "Master Data", [(report, "SELECT 1")])

        self.assertEqual(["deficiencies_parts"], [item.internalName for item in fake_nemo.created_reports])

    def test_customized_report_post_uses_same_name_and_creation_context(self) -> None:
        config = SimpleNamespace(
            get_tenant=lambda: "proalpha",
            get_config_nemo_url=lambda: "https://nemo.example",
            connection_get_headers=lambda: {"Authorization": "Bearer test"},
        )
        nemo = SimpleNamespace(config=config)
        report = _updated_report(
            {
                "id": "standard-report",
                "displayName": "(DEFICIENCIES) Customers",
                "internalName": "deficiencies_customers",
                "isCustom": False,
            },
            "SELECT 1",
        )
        response = SimpleNamespace(status_code=201, text="")

        with (
            patch("backend.services.nemo_client.getProjectID", return_value="project-1"),
            patch("backend.services.nemo_client.requests.post", return_value=response) as post_mock,
        ):
            _create_customized_report(nemo, "Master Data", report)

        payload = post_mock.call_args.kwargs["json"]
        self.assertEqual("", payload["id"])
        self.assertEqual("deficiencies_customers", payload["internalName"])
        self.assertEqual("project-1", payload["projectId"])
        self.assertEqual("proalpha", payload["tenant"])
        self.assertTrue(payload["isCustom"])

    def test_existing_custom_report_payload_keeps_update_context(self) -> None:
        report = {
            "id": "report-1",
            "displayName": "(DEFICIENCIES) Customers",
            "internalName": "deficiencies_customers",
            "tenant": "proalpha",
            "projectId": "project-1",
            "isCustom": False,
            "metadataClassificationInternalName": "classification",
        }

        payload = _updated_report(report, "SELECT 1").to_dict()

        self.assertEqual("proalpha", payload["tenant"])
        self.assertEqual("project-1", payload["projectId"])
        self.assertFalse(payload["isCustom"])
        self.assertEqual("classification", payload["metadataClassificationInternalName"])
        self.assertEqual("report-1", payload["id"])

    def test_new_report_payload_keeps_creation_context(self) -> None:
        report = {
            "id": "",
            "displayName": "(DEFICIENCIES) Customers TOP 25",
            "internalName": "deficiencies_customers_top_25",
            "tenant": "proalpha",
            "projectId": "project-1",
            "isCustom": True,
        }

        payload = _updated_report(report, "SELECT TOP 25 1").to_dict()

        self.assertEqual("proalpha", payload["tenant"])
        self.assertEqual("project-1", payload["projectId"])
        self.assertTrue(payload["isCustom"])


class FakeNemo:
    def __init__(self, columns, tenant="proalpha"):
        self.columns = columns
        self.projectname = None
        self.config = SimpleNamespace(get_tenant=lambda: tenant)

    def getColumns(self, projectname: str, filter: str = "*"):
        self.projectname = projectname
        self.filter = filter
        return self.columns

    def createReports(self, projectname: str, reports):
        self.created_project = projectname
        self.created_reports = reports


if __name__ == "__main__":
    unittest.main()
