import tempfile
import unittest
from pathlib import Path

from backend.services.rule_catalog import (
    RuleTemplateResolutionError,
    RuleTemplateValidationError,
    resolve_rule_template,
    validate_rule_template,
)
from backend.services.rule_catalog_store import RuleCatalogStore


class RuleTemplateResolverTest(unittest.TestCase):
    def test_resolves_field_messages_and_typed_parameters(self) -> None:
        version = {
            "templateId": "rule_min_length",
            "version": 2,
            "conditionTemplate": "LENGTH(TRIM({field})) < {min_length}",
            "messageDeTemplate": "{displayName} ist kürzer als {min_length} Zeichen",
            "messageEnTemplate": "{displayName} is shorter than {min_length} characters",
            "dimension": "Korrektheit",
            "ruleType": "min_length",
            "parameterSchema": {
                "min_length": {"type": "integer", "required": True, "min": 1},
            },
        }

        resolved = resolve_rule_template(
            version,
            field="ADDRESS_CITY",
            display_name="Ort",
            parameters={"min_length": 3},
        )

        self.assertEqual("LENGTH(TRIM(ADDRESS_CITY)) < 3", resolved.condition)
        self.assertEqual("Ort ist kürzer als 3 Zeichen", resolved.messageDe)
        self.assertEqual("Ort is shorter than 3 characters", resolved.messageEn)
        self.assertEqual({"min_length": 3}, resolved.parameters)

    def test_quotes_text_and_regex_parameters_for_hana_sql(self) -> None:
        version = {
            "templateId": "rule_regex",
            "version": 1,
            "conditionTemplate": "{field} NOT LIKE_REGEXPR {pattern}",
            "messageDeTemplate": "{displayName} entspricht nicht {pattern}",
            "messageEnTemplate": "{displayName} does not match {pattern}",
            "dimension": "Korrektheit",
            "ruleType": "regex",
            "parameterSchema": {
                "pattern": {"type": "regex", "required": True},
            },
        }

        resolved = resolve_rule_template(
            version,
            field="ADDRESS_NAME",
            display_name="Name",
            parameters={"pattern": "^[A-Z']+$"},
        )

        self.assertEqual("ADDRESS_NAME NOT LIKE_REGEXPR '^[A-Z'']+$'", resolved.condition)
        self.assertEqual("Name entspricht nicht ^[A-Z']+$", resolved.messageDe)

    def test_rejects_unknown_placeholders_and_unsafe_fields(self) -> None:
        with self.assertRaisesRegex(RuleTemplateValidationError, "Nicht definierte Platzhalter"):
            validate_rule_template("{field} = {unknown}", "", "", {})

        version = {
            "templateId": "rule_required",
            "version": 1,
            "conditionTemplate": "{field} IS NULL",
            "messageDeTemplate": "{displayName} fehlt",
            "messageEnTemplate": "{displayName} is missing",
            "dimension": "Vollständigkeit",
            "ruleType": "completeness",
            "parameterSchema": {},
        }
        with self.assertRaisesRegex(RuleTemplateResolutionError, "SQL-Feldname"):
            resolve_rule_template(version, field="ADDRESS_CITY; DROP TABLE")


class RuleCatalogStoreTest(unittest.TestCase):
    def test_creates_global_template_and_keeps_versions_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")
            created = store.create_template(
                key="required-field",
                name="Pflichtfeldprüfung",
                description="Prüft leere Pflichtfelder.",
                status="approved",
                condition_template="{field} IS NULL OR TRIM({field}) = ''",
                message_de_template="{displayName} ist leer",
                message_en_template="{displayName} is empty",
                dimension="Vollständigkeit",
                rule_type="completeness",
                compatible_data_types=["string"],
                field_categories=["master-data"],
                examples=[{"value": "", "deficient": True}],
            )

            updated = store.add_version(
                created.id,
                condition_template="{field} IS NULL OR LENGTH(TRIM({field})) = 0",
                message_de_template="{displayName} ist leer",
                message_en_template="{displayName} is empty",
                dimension="Vollständigkeit",
                rule_type="completeness",
                compatible_data_types=["string"],
                field_categories=["master-data"],
                examples=[{"value": None, "deficient": True}],
                change_note="Leere Zeichenketten vereinheitlicht",
            )

            first = store.get_template(created.key, version=1)
            self.assertEqual(1, created.currentVersion)
            self.assertEqual(2, updated.currentVersion)
            self.assertEqual("{field} IS NULL OR TRIM({field}) = ''", first.version.conditionTemplate)
            self.assertEqual("{field} IS NULL OR LENGTH(TRIM({field})) = 0", updated.version.conditionTemplate)
            self.assertEqual(["string"], updated.version.compatibleDataTypes)
            self.assertEqual(1, len(store.list_templates(status="approved")))

    def test_bindings_separate_global_template_from_project_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")
            template = store.create_template(
                key="minimum-length",
                name="Mindestlänge",
                condition_template="LENGTH(TRIM({field})) < {min_length}",
                message_de_template="{displayName} ist zu kurz",
                message_en_template="{displayName} is too short",
                dimension="Korrektheit",
                rule_type="min_length",
                parameter_schema={"min_length": {"type": "integer", "required": True, "min": 1}},
            )

            master_data = store.bind_rule(
                template_ref=template.id,
                template_version=1,
                config_id="config-a",
                project="Master Data",
                report_ref="customers",
                group_ref="address_city",
                rule_ref="rule-3",
                parameters={"min_length": 3},
            )
            business_processes = store.bind_rule(
                template_ref=template.id,
                template_version=1,
                config_id="config-b",
                project="Business Processes",
                report_ref="sales-orders",
                group_ref="ship_to_city",
                rule_ref="rule-8",
                parameters={"min_length": 2},
            )

            bindings = store.list_bindings(template_ref=template.key)
            self.assertEqual({"Master Data", "Business Processes"}, {binding.project for binding in bindings})
            self.assertEqual(template.id, master_data.templateId)
            self.assertEqual(template.id, business_processes.templateId)
            self.assertNotIn("config", template.to_dict())
            self.assertNotIn("project", template.to_dict())

    def test_default_catalog_contains_immediately_usable_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")

            store.ensure_default_templates()
            store.ensure_default_templates()

            templates = store.list_templates(status="approved")
            self.assertEqual(
                {"required_field", "trim_whitespace", "minimum_length", "maximum_length"},
                {template.key for template in templates},
            )
            self.assertEqual(4, len(templates))

    def test_candidate_decisions_persist_per_config_and_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            store = RuleCatalogStore(db_path)

            store.set_candidate_decision(
                config_id="config-a",
                project="Master Data",
                candidate_key="candidate-1",
                decision="rejected",
            )

            reopened = RuleCatalogStore(db_path)
            self.assertEqual(
                {"candidate-1": "rejected"},
                reopened.list_candidate_decisions(config_id="config-a", project="Master Data"),
            )
            self.assertEqual(
                {},
                reopened.list_candidate_decisions(config_id="config-b", project="Master Data"),
            )

            reopened.set_candidate_decision(
                config_id="config-a",
                project="Master Data",
                candidate_key="candidate-1",
                decision=None,
            )
            self.assertEqual(
                {},
                reopened.list_candidate_decisions(config_id="config-a", project="Master Data"),
            )


if __name__ == "__main__":
    unittest.main()
