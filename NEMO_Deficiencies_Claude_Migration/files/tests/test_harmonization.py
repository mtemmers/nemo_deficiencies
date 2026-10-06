import unittest

from backend.services.harmonization import build_harmonization_matrix, prepare_group_transfer


def _report_model(report_id, field_name=None, condition=None):
    groups = []
    if field_name:
        groups.append(
            {
                "title": f"{field_name} (Telefonnummer)",
                "displayName": "AddressTelephone",
                "internalName": field_name,
                "description": "Telefonnummer",
                "rules": [
                    {
                        "condition": condition or f"{field_name} IS NULL",
                        "message": "Telefonnummer fehlt",
                        "dimension": "Vollständigkeit",
                        "ruleType": "completeness",
                        "active": True,
                    }
                ],
            }
        )
    return {
        "report": {"internalName": report_id, "displayName": report_id},
        "model": {"checks": {"groups": groups}},
    }


class HarmonizationTest(unittest.TestCase):
    def test_equivalent_rules_with_different_internal_names_are_aligned(self) -> None:
        matrix = build_harmonization_matrix(
            [
                _report_model("customers", "ADDRESS_TELEPHONE"),
                _report_model("suppliers", "SUPPLIER_TELEPHONE"),
                _report_model("parts"),
            ],
            [
                {"internalName": "ADDRESS_TELEPHONE", "displayName": "AddressTelephone"},
                {"internalName": "SUPPLIER_TELEPHONE", "displayName": "AddressTelephone"},
            ],
        )

        field = matrix["fields"][0]
        self.assertEqual("Telefonnummer", field["designation"])
        self.assertEqual("aligned", field["reports"]["customers"]["status"])
        self.assertEqual("aligned", field["reports"]["suppliers"]["status"])
        self.assertEqual(1, field["missingReportCount"])

    def test_different_rule_set_is_marked_divergent(self) -> None:
        matrix = build_harmonization_matrix(
            [
                _report_model("customers", "ADDRESS_TELEPHONE"),
                _report_model(
                    "suppliers",
                    "SUPPLIER_TELEPHONE",
                    "LENGTH(SUPPLIER_TELEPHONE) > 30",
                ),
            ],
            [
                {"internalName": "ADDRESS_TELEPHONE", "displayName": "AddressTelephone"},
                {"internalName": "SUPPLIER_TELEPHONE", "displayName": "AddressTelephone"},
            ],
        )

        statuses = {entry["status"] for entry in matrix["fields"][0]["reports"].values()}
        self.assertEqual({"aligned", "divergent"}, statuses)
        self.assertEqual(1, matrix["summary"]["divergentCount"])
        field = matrix["fields"][0]
        self.assertEqual("customers", field["referenceReportId"])
        differences = field["reports"]["suppliers"]["differences"]
        self.assertEqual("condition", differences[0]["property"])
        self.assertEqual("ADDRESS_TELEPHONE IS NULL", differences[0]["referenceValue"])
        self.assertEqual("LENGTH(SUPPLIER_TELEPHONE) > 30", differences[0]["currentValue"])

    def test_different_messages_are_exposed_for_detail_view(self) -> None:
        source = _report_model("customers", "ADDRESS_TELEPHONE")
        target = _report_model("suppliers", "SUPPLIER_TELEPHONE")
        target["model"]["checks"]["groups"][0]["rules"][0]["message"] = "TELEFON fehlt"

        matrix = build_harmonization_matrix(
            [source, target],
            [
                {"internalName": "ADDRESS_TELEPHONE", "displayName": "AddressTelephone"},
                {"internalName": "SUPPLIER_TELEPHONE", "displayName": "AddressTelephone"},
            ],
        )

        differences = matrix["fields"][0]["reports"]["suppliers"]["differences"]
        self.assertEqual(
            {
                "ruleNumber": 1,
                "property": "message",
                "referenceValue": "Telefonnummer fehlt",
                "currentValue": "TELEFON fehlt",
            },
            differences[0],
        )

    def test_transfer_replaces_rules_and_adapts_target_internal_name(self) -> None:
        source = _report_model("customers", "ADDRESS_TELEPHONE")
        target = _report_model("suppliers", "SUPPLIER_TELEPHONE", "LENGTH(SUPPLIER_TELEPHONE) > 30")

        plan = prepare_group_transfer(
            [source, target],
            [
                {"internalName": "ADDRESS_TELEPHONE", "displayName": "AddressTelephone"},
                {"internalName": "SUPPLIER_TELEPHONE", "displayName": "AddressTelephone"},
            ],
            "addresstelephone",
            "customers",
            ["suppliers"],
        )

        change = plan["changes"][0]
        group = change["editorModel"]["checks"]["groups"][0]
        self.assertEqual("replace", change["action"])
        self.assertEqual("SUPPLIER_TELEPHONE", group["internalName"])
        self.assertEqual("SUPPLIER_TELEPHONE IS NULL", group["rules"][0]["condition"])
        self.assertEqual(1, change["newRuleCount"])

    def test_transfer_creates_missing_group_and_source_attribute(self) -> None:
        source = _report_model("customers", "ADDRESS_TELEPHONE")
        target = _report_model("parts")
        target["model"]["source"] = {"attributes": []}

        plan = prepare_group_transfer(
            [source, target],
            [{"internalName": "ADDRESS_TELEPHONE", "displayName": "AddressTelephone"}],
            "addresstelephone",
            "customers",
            ["parts"],
        )

        change = plan["changes"][0]
        self.assertEqual("create", change["action"])
        self.assertEqual("ADDRESS_TELEPHONE", change["editorModel"]["source"]["attributes"][0]["name"])
        self.assertEqual(1, plan["summary"]["createCount"])

    def test_rule_expression_resolves_group_without_header_internal_name(self) -> None:
        contacts = _report_model("contacts", "ADDRESS_STREET")
        group = contacts["model"]["checks"]["groups"][0]
        group["internalName"] = ""
        group["field"] = ""
        group["rules"][0]["expression"] = "ADDRESS_STREET"

        matrix = build_harmonization_matrix(
            [contacts],
            [{"internalName": "ADDRESS_STREET", "displayName": "AddressStreet"}],
        )

        self.assertEqual(1, matrix["summary"]["fieldCount"])
        self.assertIn("contacts", matrix["fields"][0]["reports"])
        self.assertEqual("ADDRESS_STREET", matrix["fields"][0]["reports"]["contacts"]["internalName"])


if __name__ == "__main__":
    unittest.main()
