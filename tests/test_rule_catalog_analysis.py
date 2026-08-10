import unittest

from backend.services.rule_catalog_analysis import analyze_rule_catalog_candidates


class RuleCatalogAnalysisTest(unittest.TestCase):
    def test_generalizes_fields_and_groups_equivalent_rules(self) -> None:
        result = analyze_rule_catalog_candidates(
            [
                _report("customers", "ADDRESS_CITY", "Ort", "ADDRESS_CITY IS NULL", "Ort leer"),
                _report("suppliers", "SUPPLIER_CITY", "Stadt", "SUPPLIER_CITY IS NULL", "Stadt leer"),
            ],
            [],
        )

        self.assertEqual(2, result["summary"]["ruleCount"])
        self.assertEqual(1, result["summary"]["candidateCount"])
        candidate = result["candidates"][0]
        self.assertEqual("{field} IS NULL", candidate["conditionTemplate"])
        self.assertEqual("{displayName} leer", candidate["messageDeTemplate"])
        self.assertEqual(2, candidate["occurrenceCount"])
        self.assertEqual(2, candidate["fieldCount"])

    def test_marks_matching_catalog_template_as_existing(self) -> None:
        template = _template("{field} IS NULL", "Vollständigkeit", "completeness")
        result = analyze_rule_catalog_candidates(
            [_report("customers", "ADDRESS_CITY", "Ort", "ADDRESS_CITY IS NULL", "Ort leer")],
            [template],
        )

        candidate = result["candidates"][0]
        self.assertEqual("template-1", candidate["existingTemplateId"])
        self.assertEqual(0, result["summary"]["newCandidateCount"])

    def test_parameterizes_and_groups_different_length_values(self) -> None:
        reports = [
            _report("customers", "ADDRESS_CITY", "Ort", "LENGTH(TRIM(ADDRESS_CITY)) < 2", "Ort kürzer als 2 Zeichen"),
            _report("suppliers", "SUPPLIER_CITY", "Stadt", "LENGTH(TRIM(SUPPLIER_CITY)) < 5", "Stadt kürzer als 5 Zeichen"),
        ]
        for report in reports:
            report["model"]["checks"]["groups"][0]["rules"][0]["ruleType"] = "min_length"
            report["model"]["checks"]["groups"][0]["rules"][0]["dimension"] = "Korrektheit"

        result = analyze_rule_catalog_candidates(reports, [])

        self.assertEqual(1, result["summary"]["candidateCount"])
        candidate = result["candidates"][0]
        self.assertEqual("LENGTH(TRIM({field})) < {min_length}", candidate["conditionTemplate"])
        self.assertEqual(
            {"min_length": {"type": "integer", "required": True, "min": 0}},
            candidate["parameterSchema"],
        )
        self.assertEqual("{displayName} kürzer als {min_length} Zeichen", candidate["messageDeTemplate"])
        self.assertEqual(
            [{"value": 2, "count": 1}, {"value": 5, "count": 1}],
            candidate["parameterVariants"]["min_length"],
        )
        self.assertEqual(
            [{"min_length": 2}, {"min_length": 5}],
            [location["parameters"] for location in candidate["locations"]],
        )

    def test_parameterizes_regex_literals_without_merging_other_sql_shapes(self) -> None:
        reports = [
            _report("customers", "EMAIL", "E-Mail", "EMAIL NOT LIKE_REGEXPR '^[A-Z]+$' FLAG 'i'", "E-Mail ungültig"),
            _report("suppliers", "MAIL", "E-Mail", "MAIL NOT LIKE_REGEXPR '^[0-9]+$' FLAG 'i'", "E-Mail ungültig"),
            _report("contacts", "MAIL", "E-Mail", "TRIM(MAIL) NOT LIKE_REGEXPR '^[0-9]+$'", "E-Mail ungültig"),
        ]
        for report in reports:
            report["model"]["checks"]["groups"][0]["rules"][0]["ruleType"] = "regex"
            report["model"]["checks"]["groups"][0]["rules"][0]["dimension"] = "Korrektheit"

        result = analyze_rule_catalog_candidates(reports, [])

        self.assertEqual(2, result["summary"]["candidateCount"])
        grouped = next(candidate for candidate in result["candidates"] if candidate["occurrenceCount"] == 2)
        self.assertEqual("{field} NOT LIKE_REGEXPR {pattern} FLAG 'i'", grouped["conditionTemplate"])
        self.assertEqual({"pattern": {"type": "regex", "required": True}}, grouped["parameterSchema"])
        self.assertEqual(2, len(grouped["parameterVariants"]["pattern"]))


def _report(report_ref, field, display_name, condition, message):
    return {
        "report": {"internalName": report_ref, "displayName": report_ref.title()},
        "model": {
            "checks": {
                "groups": [
                    {
                        "id": f"group-{field}",
                        "title": f"{field} ({display_name})",
                        "displayName": display_name,
                        "internalName": field,
                        "rules": [
                            {
                                "id": f"rule-{field}",
                                "condition": condition,
                                "message": message,
                                "dimension": "Vollständigkeit",
                                "ruleType": "completeness",
                                "active": True,
                            }
                        ],
                    }
                ]
            }
        },
    }


def _template(condition, dimension, rule_type):
    version = type(
        "Version",
        (),
        {
            "conditionTemplate": condition,
            "dimension": dimension,
            "ruleType": rule_type,
        },
    )()
    return type("Template", (), {"id": "template-1", "name": "Vorlage", "version": version})()


if __name__ == "__main__":
    unittest.main()
