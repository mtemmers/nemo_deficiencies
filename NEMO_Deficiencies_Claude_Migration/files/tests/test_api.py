import unittest
from contextlib import contextmanager
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException

from backend.main import (
    AIRuleExampleTestRequest,
    AIRuleExplanationRequest,
    AIMessageTranslationRequest,
    ConfigConnectionUpdateRequest,
    ConfigCredentialsRequest,
    EditorModelRequest,
    EditorUndoRequest,
    HarmonizationTransferRequest,
    NemoReportWriteRequest,
    ReportExportRequest,
    RuleCatalogAnalysisRequest,
    RuleCatalogCandidateDecisionRequest,
    RuleCatalogImportRequest,
    RuleTemplateBindingRequest,
    RuleTemplateResolveRequest,
    _resolve_top_25_report,
    _load_reports,
    _nemo_error_summary,
    _sql_export_filename,
    health,
    get_config_statistics,
    get_editor_model,
    apply_harmonization_transfer,
    analyze_existing_rule_templates,
    bind_catalog_rule,
    create_config_from_credentials,
    delete_config,
    get_config_connection,
    import_existing_rule_templates,
    list_configs,
    list_projects,
    list_rule_templates,
    resolve_catalog_rule,
    render_report_sql,
    run_cli_wizard_export,
    restore_original_report,
    set_rule_template_candidate_decision,
    translate_ai_messages,
    update_config_connection,
    write_report_to_nemo,
)
from backend.services.editor_baseline_store import EditorBaselineStore
from backend.services.editor_draft_store import EditorDraftStore
from backend.services.editor_change_log_store import EditorChangeLogStore
from backend.services.ai_translation_cache_store import AITranslationCacheStore
from backend.services.config_store import ConfigStore, read_nemo_config_settings
from backend.services.rule_catalog_store import RuleCatalogStore
from backend.services.sql_model import parse_editor_model


class ApiTest(unittest.TestCase):
    def test_cli_export_uses_tenant_subdirectory(self) -> None:
        @contextmanager
        def tenant_context():
            yield SimpleNamespace(id="config-1", tenant="Tenant:/Name*", name="Config"), object()

        result_payload = {
            "outputDir": "unused",
            "selectedReportCount": 1,
            "catalogReportCount": 1,
            "sqlFileCount": 1,
            "dataFileCount": 0,
            "dataErrorCount": 0,
            "indexFile": "index.csv",
            "metadataFile": "metadata.json",
        }
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("backend.main._nemo_for_config", return_value=tenant_context()),
            patch("backend.main.get_reports", return_value=[{"id": "report-1"}]),
            patch("backend.main.export_reports", return_value=result_payload) as export_mock,
        ):
            response = run_cli_wizard_export(
                ReportExportRequest(
                    configId="config-1",
                    action="sql",
                    selectionMode="all",
                    outputDir=temp_dir,
                )
            )

        self.assertEqual("Tenant:/Name*", response["tenant"])
        self.assertEqual(Path(temp_dir).resolve() / "Tenant_Name", export_mock.call_args.kwargs["output_dir"])

    def test_connection_config_can_be_created_read_updated_and_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConfigStore(Path(temp_dir))
            with patch("backend.main._store", return_value=store):
                created = create_config_from_credentials(
                    ConfigCredentialsRequest(
                        name="NextGen Demo",
                        tenant="nextgendemo",
                        userid="demo-user",
                        password="initial-secret",
                        nemoUrl="https://nextgendemo.enter.nemo-ai.com",
                        environment="nextgendemo",
                    )
                )["config"]
                visible = get_config_connection(created["id"])["config"]

                self.assertEqual("demo-user", visible["userid"])
                self.assertEqual("https://nextgendemo.enter.nemo-ai.com", visible["nemoUrl"])
                self.assertEqual("nextgendemo", visible["environment"])
                self.assertTrue(visible["hasPassword"])
                self.assertNotIn("password", visible)

                updated = update_config_connection(
                    created["id"],
                    ConfigConnectionUpdateRequest(
                        name="NextGen Demo geändert",
                        tenant="nextgendemo",
                        userid="new-user",
                        password="replacement-secret",
                        nemoUrl="https://test.enter.nemo-ai.com/",
                        environment="test",
                    ),
                )
                stored = read_nemo_config_settings(store.decrypt_config(created["id"]))
                self.assertEqual("NextGen Demo geändert", updated["config"]["name"])
                self.assertEqual("new-user", stored["userid"])
                self.assertEqual("https://test.enter.nemo-ai.com", stored["nemoUrl"])
                self.assertNotIn(b"replacement-secret", store.db_path.read_bytes())

                delete_config(created["id"])
                self.assertEqual([], store.list_profiles())

    def test_report_authentication_error_points_to_config_editor(self) -> None:
        with (
            patch("backend.main._nemo_for_config", return_value=fake_nemo_context()),
            patch(
                "backend.main.get_reports",
                side_effect=Exception(
                    'request failed. Status: 400, error: {"__type":"NotAuthorizedException",'
                    '"message":"Incorrect username or password."}'
                ),
            ),
        ):
            with self.assertRaises(HTTPException) as raised:
                _load_reports("config-1", "Master Data", True)

        self.assertEqual(401, raised.exception.status_code)
        self.assertIn("Konfiguration bearbeiten", raised.exception.detail)

    def test_config_statistics_summarizes_reports_groups_and_rule_status(self) -> None:
        first = harmonization_report_model("customers", "ADDRESS_CITY", "ADDRESS_CITY IS NULL")
        second = harmonization_report_model("suppliers", "SUPPLIER_CITY", "SUPPLIER_CITY IS NULL")
        second["model"]["checks"]["groups"][0]["rules"].append(
            {
                "condition": "LENGTH(SUPPLIER_CITY) < 2",
                "message": "Ort zu kurz",
                "dimension": "Korrektheit",
                "ruleType": "min_length",
                "active": False,
            }
        )
        profile = SimpleNamespace(id="config-1", name="Test", tenant="test.example")
        with patch(
            "backend.main._load_harmonization_context",
            return_value=(profile, [first, second], [], [{"reportRef": "broken"}]),
        ):
            result = get_config_statistics(config_id="config-1", project="Master Data")

        self.assertEqual(2, result["summary"]["reportCount"])
        self.assertEqual(2, result["summary"]["groupCount"])
        self.assertEqual(3, result["summary"]["ruleCount"])
        self.assertEqual(2, result["summary"]["activeRuleCount"])
        self.assertEqual(1, result["summary"]["inactiveRuleCount"])
        self.assertEqual(1, result["summary"]["skippedReportCount"])
        self.assertEqual("test.example", result["configTenant"])
        self.assertEqual(2, len(result["reports"]))

    def test_foreign_editor_draft_is_removed_and_cannot_be_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data.sqlite"
            draft_store = EditorDraftStore(db_path)
            baseline_store = EditorBaselineStore(db_path)
            profile = SimpleNamespace(id="config-1")
            customer_report = report_with_source(
                "customer-id",
                "deficiencies_customers",
                "(DEFICIENCIES) Customers",
                "customer_source",
            )
            address_report = report_with_source(
                "address-id",
                "deficiencies_addresses",
                "(DEFICIENCIES) Addresses",
                "address_source",
            )
            address_model = parse_editor_model(address_report["querySyntax"], address_report)
            draft_store.save_draft(
                "config-1",
                "Master Data",
                "deficiencies_customers",
                address_model,
            )

            with patch(
                "backend.main._load_reports",
                return_value=(profile, [customer_report]),
            ), patch(
                "backend.main._draft_store",
                return_value=draft_store,
            ), patch(
                "backend.main._baseline_store",
                return_value=baseline_store,
            ):
                payload = get_editor_model(
                    "deficiencies_customers",
                    config_id="config-1",
                    project="Master Data",
                )
                with self.assertRaises(HTTPException) as raised:
                    render_report_sql(
                        "deficiencies_customers",
                        EditorModelRequest(
                            configId="config-1",
                            project="Master Data",
                            editorModel=address_model,
                        ),
                    )

            source_block = next(
                block for block in payload["editorModel"]["blocks"] if block["id"] == "source"
            )
            self.assertEqual("imported-report-sql", payload["source"])
            self.assertIsNone(payload["draft"])
            self.assertEqual("customer_source", source_block["cteName"])
            self.assertIsNone(
                draft_store.get_draft("config-1", "Master Data", "deficiencies_customers")
            )
            self.assertEqual(409, raised.exception.status_code)
            self.assertIn("anderen Bericht", str(raised.exception.detail))

    def test_stale_draft_is_archived_when_nemo_report_sql_changed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data.sqlite"
            draft_store = EditorDraftStore(db_path)
            baseline_store = EditorBaselineStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            profile = SimpleNamespace(id="config-1")
            old_report = report_with_source(
                "customer-id",
                "deficiencies_customers",
                "(DEFICIENCIES) Customers",
                "customer_source",
            )
            current_report = report_with_source(
                "customer-id",
                "deficiencies_customers",
                "(DEFICIENCIES) Customers",
                "customer_source_v2",
            )
            old_model = parse_editor_model(old_report["querySyntax"], old_report)
            baseline_store.capture_if_missing(
                "config-1",
                "Master Data",
                "deficiencies_customers",
                old_report["querySyntax"],
                old_model,
            )
            draft_store.save_draft(
                "config-1",
                "Master Data",
                "deficiencies_customers",
                old_model,
            )

            with patch(
                "backend.main._load_reports",
                return_value=(profile, [current_report]),
            ), patch(
                "backend.main._draft_store",
                return_value=draft_store,
            ), patch(
                "backend.main._baseline_store",
                return_value=baseline_store,
            ), patch(
                "backend.main._change_store",
                return_value=change_store,
            ):
                payload = get_editor_model(
                    "deficiencies_customers",
                    config_id="config-1",
                    project="Master Data",
                )

            source_block = next(
                block for block in payload["editorModel"]["blocks"] if block["id"] == "source"
            )
            self.assertEqual("imported-report-sql", payload["source"])
            self.assertTrue(payload["staleDraftDiscarded"])
            self.assertIsNone(payload["draft"])
            self.assertEqual("customer_source_v2", source_block["cteName"])
            self.assertIsNone(
                draft_store.get_draft("config-1", "Master Data", "deficiencies_customers")
            )
            archived = change_store.list_changes(
                "config-1", "Master Data", "deficiencies_customers"
            )[0]
            self.assertEqual("external_report_refresh", archived.changeType)
            self.assertIsNotNone(archived.undoneAt)
            self.assertEqual(old_report["querySyntax"], baseline_store.get_baseline(
                "config-1", "Master Data", "deficiencies_customers"
            ).originalSql)

    def test_existing_rules_can_be_analyzed_and_imported_as_catalog_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "catalog.sqlite")
            store.ensure_default_templates()
            reports = [
                harmonization_report_model("customers", "ADDRESS_CITY", "LENGTH(ADDRESS_CITY) = 13"),
                harmonization_report_model("suppliers", "SUPPLIER_CITY", "LENGTH(SUPPLIER_CITY) = 13"),
            ]
            context = (SimpleNamespace(id="config-1"), reports, [], [])
            analysis_request = RuleCatalogAnalysisRequest(configId="config-1", project="Master Data")

            with patch("backend.main._load_harmonization_context", return_value=context), patch(
                "backend.main._rule_template_store", return_value=store
            ):
                analysis = analyze_existing_rule_templates(analysis_request)
                candidate = next(item for item in analysis["candidates"] if not item["existingTemplateId"])
                imported = import_existing_rule_templates(
                    RuleCatalogImportRequest(
                        configId="config-1",
                        project="Master Data",
                        candidateKeys=[candidate["key"]],
                    )
                )

            self.assertEqual(2, candidate["occurrenceCount"])
            self.assertEqual("LENGTH({field}) = 13", candidate["conditionTemplate"])
            self.assertEqual(1, imported["createdCount"])
            self.assertEqual(2, imported["bindingCount"])
            self.assertEqual("draft", imported["imported"][0]["template"]["status"])

    def test_parameterized_existing_rules_keep_values_in_catalog_bindings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "catalog.sqlite")
            store.ensure_default_templates()
            reports = [
                harmonization_report_model("customers", "ADDRESS_CITY", "LENGTH(TRIM(ADDRESS_CITY)) < 2"),
                harmonization_report_model("suppliers", "SUPPLIER_CITY", "LENGTH(TRIM(SUPPLIER_CITY)) < 5"),
            ]
            for report in reports:
                rule = report["model"]["checks"]["groups"][0]["rules"][0]
                rule["ruleType"] = "min_length"
                rule["dimension"] = "Korrektheit"
            context = (SimpleNamespace(id="config-1"), reports, [], [])
            analysis_request = RuleCatalogAnalysisRequest(configId="config-1", project="Master Data")

            with patch("backend.main._load_harmonization_context", return_value=context), patch(
                "backend.main._rule_template_store", return_value=store
            ):
                analysis = analyze_existing_rule_templates(analysis_request)
                candidate = analysis["candidates"][0]
                imported = import_existing_rule_templates(
                    RuleCatalogImportRequest(
                        configId="config-1",
                        project="Master Data",
                        candidateKeys=[candidate["key"]],
                    )
                )

            bindings = store.list_bindings(template_ref="minimum_length")
            self.assertTrue(candidate["existingTemplateId"])
            self.assertEqual(0, imported["createdCount"])
            self.assertEqual(
                [{"min_length": 2}, {"min_length": 5}],
                sorted((binding.parameters for binding in bindings), key=lambda item: item["min_length"]),
            )

    def test_candidate_rejection_is_returned_by_followup_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "catalog.sqlite")
            store.ensure_default_templates()
            reports = [
                harmonization_report_model("customers", "ADDRESS_CITY", "LENGTH(ADDRESS_CITY) = 13"),
            ]
            context = (SimpleNamespace(id="config-1"), reports, [], [])
            analysis_request = RuleCatalogAnalysisRequest(configId="config-1", project="Master Data")

            with patch("backend.main._load_harmonization_context", return_value=context), patch(
                "backend.main._rule_template_store", return_value=store
            ):
                first = analyze_existing_rule_templates(analysis_request)
                candidate_key = first["candidates"][0]["key"]
                decision = set_rule_template_candidate_decision(
                    RuleCatalogCandidateDecisionRequest(
                        configId="config-1",
                        project="Master Data",
                        candidateKey=candidate_key,
                        decision="rejected",
                    )
                )
                second = analyze_existing_rule_templates(analysis_request)

            self.assertEqual("rejected", decision["decision"])
            self.assertEqual("rejected", second["candidates"][0]["decision"])

    def test_rule_template_api_lists_resolves_and_binds_global_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RuleCatalogStore(Path(temp_dir) / "catalog.sqlite")
            store.ensure_default_templates()
            resolve_request = RuleTemplateResolveRequest(
                version=1,
                field="ADDRESS_CITY",
                displayName="Ort",
                parameters={"min_length": 3},
            )
            binding_request = RuleTemplateBindingRequest(
                templateId="minimum-length",
                templateVersion=1,
                configId="config-1",
                project="Master Data",
                reportRef="customers",
                groupRef="address_city",
                ruleRef="rule-1",
                parameters={"min_length": 3},
            )

            with patch("backend.main._rule_template_store", return_value=store):
                listed = list_rule_templates(status=None)
                resolved = resolve_catalog_rule("minimum-length", resolve_request)
                bound = bind_catalog_rule(binding_request)

            self.assertEqual(4, listed["count"])
            self.assertEqual("LENGTH(TRIM(ADDRESS_CITY)) < 3", resolved["resolvedRule"]["condition"])
            self.assertEqual("Master Data", bound["binding"]["project"])

    def test_harmonization_apply_persists_undoable_target_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data.sqlite"
            draft_store = EditorDraftStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            reports = [
                harmonization_report_model("customers", "ADDRESS_CITY", "ADDRESS_CITY IS NULL"),
                harmonization_report_model("suppliers", "SUPPLIER_CITY", "LENGTH(SUPPLIER_CITY) > 40"),
            ]
            columns = [
                {"internalName": "ADDRESS_CITY", "displayName": "AddressCity"},
                {"internalName": "SUPPLIER_CITY", "displayName": "AddressCity"},
            ]
            request = HarmonizationTransferRequest(
                configId="config-1",
                project="Master Data",
                fieldKey="addresscity",
                sourceReportId="customers",
                targetReportIds=["suppliers"],
            )
            with patch(
                "backend.main._load_harmonization_context",
                return_value=(SimpleNamespace(id="config-1"), reports, columns, []),
            ), patch("backend.main._draft_store", return_value=draft_store), patch(
                "backend.main._change_store", return_value=change_store
            ), patch("backend.main._editor_storage_ref", side_effect=lambda _c, _p, report_ref: report_ref):
                result = apply_harmonization_transfer(request)

            draft = draft_store.get_draft("config-1", "Master Data", "suppliers")
            self.assertEqual(1, len(result["applied"]))
            self.assertEqual("SUPPLIER_CITY IS NULL", draft.editorModel["checks"]["groups"][0]["rules"][0]["condition"])
            change = change_store.latest_undoable_change("config-1", "Master Data", "suppliers")
            self.assertEqual("harmonization_group_replace", change.changeType)
            self.assertEqual("$", change.targetPath)

    def test_message_translation_uses_persistent_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AITranslationCacheStore(Path(temp_dir) / "cache.sqlite")
            connector = Mock()
            connector.settings = SimpleNamespace(provider="gemini", model="fast-model")
            connector.translate_messages.return_value = {
                "targetLanguage": "en",
                "translations": [{"id": "1", "text": "Customer number is missing"}],
            }
            request = AIMessageTranslationRequest(
                configId="config-1",
                aiConfigId="ai-1",
                targetLanguage="en",
                messages=[{"id": "1", "text": "Kundennummer fehlt", "sourceLanguage": "de"}],
            )

            with patch("backend.main._resolve_ai_connector", return_value=(SimpleNamespace(id="config-1"), connector)), patch(
                "backend.main._translation_cache_store", return_value=cache
            ):
                first = translate_ai_messages(request)
                second = translate_ai_messages(request)

            self.assertEqual({"hits": 0, "misses": 1}, first["cache"])
            self.assertEqual({"hits": 1, "misses": 0}, second["cache"])
            self.assertEqual(1, connector.translate_messages.call_count)

    def test_existing_ai_rule_requests_accept_long_hana_conditions(self) -> None:
        condition = "FIELD NOT LIKE_REGEXPR 'x' OR " * 1800

        explanation = AIRuleExplanationRequest(internalName="FIELD", condition=condition)
        example_test = AIRuleExampleTestRequest(
            internalName="FIELD",
            condition=condition,
            examples=[{"value": "x", "expectedViolation": False}],
        )

        self.assertGreater(len(explanation.condition), 4000)
        self.assertEqual(condition, example_test.condition)

    def test_health(self) -> None:
        payload = health()
        self.assertEqual("ok", payload["status"])
        self.assertRegex(payload["version"], r"^\d+\.\d+\.\d+$")

    def test_projects_contains_standard_projects(self) -> None:
        data = list_projects()

        self.assertEqual("Master Data", data["defaultProject"])
        self.assertEqual(["Master Data", "Business Processes"], [project["id"] for project in data["projects"]])

    def test_sql_export_filename_is_safe(self) -> None:
        self.assertEqual("deficiencies_customers_top_25.sql", _sql_export_filename({"internalName": "deficiencies_customers_top_25"}))
        self.assertEqual("DEFICIENCIES_Customers_TOP_25.sql", _sql_export_filename({"displayName": "(DEFICIENCIES) Customers TOP 25"}))

    def test_nemo_error_summary_extracts_api_detail(self) -> None:
        error = ValueError(
            'PUT Request failed. Status: 500, error: {"Detail":"One of projectId or templateId must be set"}'
        )

        self.assertEqual(
            "One of projectId or templateId must be set",
            _nemo_error_summary(error),
        )

    def test_configs_do_not_expose_file_paths_or_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConfigStore(Path(temp_dir))
            store.create_config(
                "test-config",
                "[nemo_library]\ntenant=test\nuserid=test-user\npassword=test-secret\n",
            )
            with patch("backend.main._store", return_value=store):
                data = list_configs()

        self.assertTrue(data["configs"])
        for config in data["configs"]:
            self.assertIn("id", config)
            self.assertIn("name", config)
            self.assertIn("source", config)
            self.assertIn("sourceFile", config)
            self.assertIn("tenant", config)
            self.assertNotIn("path", config)
            self.assertNotIn("iniContent", config)
            self.assertNotIn("encrypted_ini", config)
            self.assertNotIn("password", config)
            self.assertNotIn("url", config)

    def test_write_to_nemo_rejects_wrong_confirmation(self) -> None:
        request = NemoReportWriteRequest(
            configId="config-1",
            project="Master Data",
            editorModel={"checks": {"groups": []}},
            overwriteConfirmation="wrong_report",
        )
        with (
            patch("backend.main._render_sql_payload", return_value=rendered_payload()),
            patch("backend.main._nemo_for_config", return_value=fake_nemo_context()),
            patch("backend.main.get_reports", return_value=[existing_report()]),
            patch("backend.main.update_reports_sql") as update_mock,
        ):
            with self.assertRaises(HTTPException) as raised:
                write_report_to_nemo("report-1", request)

        self.assertEqual(409, raised.exception.status_code)
        update_mock.assert_not_called()

    def test_write_to_nemo_updates_exact_existing_report(self) -> None:
        request = NemoReportWriteRequest(
            configId="config-1",
            project="Master Data",
            editorModel={"checks": {"groups": []}},
            overwriteConfirmation="deficiencies_customers",
        )
        with (
            patch("backend.main._render_sql_payload", return_value=rendered_payload()),
            patch("backend.main._nemo_for_config", return_value=fake_nemo_context()),
            patch("backend.main.get_reports", return_value=[existing_report(), top_25_report()]),
            patch("backend.main._baseline_store"),
            patch("backend.main.update_reports_sql") as update_mock,
        ):
            result = write_report_to_nemo("report-1", request)

        self.assertEqual("updated", result["status"])
        self.assertEqual("deficiencies_customers", result["internalName"])
        update_mock.assert_called_once()
        updates = update_mock.call_args.kwargs["updates"]
        self.assertEqual(2, len(updates))
        self.assertEqual("deficiencies_customers", updates[0][0]["internalName"])
        self.assertEqual("deficiencies_customers_top_25", updates[1][0]["internalName"])
        self.assertIn("SELECT TOP 25", updates[1][1])
        self.assertTrue(updates[1][1].rstrip().endswith("ORDER BY ERROREVALUATION DESC"))
        self.assertEqual(2, len(result["updatedReports"]))

    def test_write_to_nemo_creates_top_25_partner_when_missing(self) -> None:
        request = NemoReportWriteRequest(
            configId="config-1",
            project="Master Data",
            editorModel={"checks": {"groups": []}},
            overwriteConfirmation="deficiencies_customers",
        )
        with (
            patch("backend.main._render_sql_payload", return_value=rendered_payload()),
            patch("backend.main._nemo_for_config", return_value=fake_nemo_context()),
            patch("backend.main.get_reports", return_value=[existing_report()]),
            patch("backend.main._baseline_store"),
            patch("backend.main.update_reports_sql") as update_mock,
        ):
            result = write_report_to_nemo("report-1", request)

        updates = update_mock.call_args.kwargs["updates"]
        self.assertEqual(2, len(updates))
        self.assertEqual("", updates[1][0]["id"])
        self.assertEqual("(DEFICIENCIES) Customers TOP 25", updates[1][0]["displayName"])
        self.assertEqual("deficiencies_customers_top_25", updates[1][0]["internalName"])
        self.assertTrue(result["top25Created"])
        self.assertTrue(result["operationId"])

    def test_top_25_partner_matches_german_and_english_names(self) -> None:
        german_top_25 = {
            **top_25_report(),
            "displayName": "(DEFICIENCIES) Kunden TOP 25",
            "internalName": "deficiencies_kunden_top_25",
        }

        report, created, strategy = _resolve_top_25_report(
            [existing_report(), german_top_25],
            existing_report(),
        )

        self.assertEqual("deficiencies_kunden_top_25", report["internalName"])
        self.assertFalse(created)
        self.assertEqual("translated", strategy)

    def test_top_25_partner_matches_all_supported_german_subjects(self) -> None:
        pairs = [
            ("Customers", "Kunden"),
            ("Suppliers", "Lieferanten"),
            ("Parts", "Teile"),
            ("Addresses", "Adressen"),
            ("Contacts", "Kontakte"),
        ]
        for english, german in pairs:
            with self.subTest(english=english):
                source = {
                    "id": f"source-{english}",
                    "displayName": f"(DEFICIENCIES) {english}",
                    "internalName": f"deficiencies_{english.casefold()}",
                }
                partner = {
                    "id": f"top-{german}",
                    "displayName": f"(DEFICIENCIES) {german} TOP 25",
                    "internalName": f"deficiencies_{german.casefold()}_top_25",
                }

                report, created, strategy = _resolve_top_25_report([source, partner], source)

                self.assertEqual(partner["id"], report["id"])
                self.assertFalse(created)
                self.assertEqual("translated", strategy)

    def test_write_to_nemo_does_not_require_second_partner_for_selected_top_25(self) -> None:
        report = top_25_report()
        payload = {**rendered_payload(), "report": report}
        request = NemoReportWriteRequest(
            configId="config-1",
            project="Master Data",
            editorModel={"checks": {"groups": []}},
            overwriteConfirmation="deficiencies_customers_top_25",
        )
        with (
            patch("backend.main._render_sql_payload", return_value=payload),
            patch("backend.main._nemo_for_config", return_value=fake_nemo_context()),
            patch("backend.main.get_reports", return_value=[report]),
            patch("backend.main._baseline_store"),
            patch("backend.main.update_reports_sql") as update_mock,
        ):
            result = write_report_to_nemo("report-top-25", request)

        updates = update_mock.call_args.kwargs["updates"]
        self.assertEqual(1, len(updates))
        self.assertEqual("deficiencies_customers_top_25", updates[0][0]["internalName"])
        self.assertEqual(1, len(result["updatedReports"]))

    def test_restore_original_report_replaces_draft_and_logs_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            original = editor_model("Ursprung")
            changed = editor_model("Bearbeitet")
            EditorBaselineStore(db_path).capture_if_missing(
                "config-1", "Master Data", "report-1", "SELECT 1", original
            )
            EditorDraftStore(db_path).save_draft("config-1", "Master Data", "report-1", changed)
            fake_store = SimpleNamespace(
                db_path=db_path,
                resolve_profile=lambda _config_id: SimpleNamespace(id="config-1"),
            )

            with patch("backend.main._store", return_value=fake_store):
                result = restore_original_report(
                    "report-1",
                    EditorUndoRequest(configId="config-1", project="Master Data"),
                )

            self.assertEqual("Ursprung", result["editorModel"]["checks"]["groups"][0]["rules"][0]["message"])
            self.assertEqual("restore_original", result["restoredChange"]["changeType"])
            self.assertEqual("$", result["restoredChange"]["targetPath"])


def existing_report() -> dict:
    return {
        "id": "report-1",
        "displayName": "(DEFICIENCIES) Customers",
        "internalName": "deficiencies_customers",
        "querySyntax": "SELECT 1 AS ERROREVALUATION FROM DUMMY",
    }


def report_with_source(report_id: str, internal_name: str, display_name: str, source_name: str) -> dict:
    return {
        "id": report_id,
        "displayName": display_name,
        "internalName": internal_name,
        "querySyntax": f"""
WITH {source_name} AS (
    SELECT NAME, MASTER_DATA_SUB_TYPE
    FROM $schema.$table
    WHERE UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
),
checks AS (
    SELECT j.*, '' AS DEFICIENCY_DESCRIPTION
    FROM {source_name} j
)
SELECT DEFICIENCY_DESCRIPTION AS RULEDESCRIPTION
FROM checks
""",
    }


def top_25_report() -> dict:
    return {
        "id": "report-top-25",
        "displayName": "(DEFICIENCIES) Customers TOP 25",
        "internalName": "deficiencies_customers_top_25",
        "querySyntax": "SELECT TOP 25 1 AS ERROREVALUATION FROM DUMMY ORDER BY ERROREVALUATION DESC",
    }


def rendered_payload() -> dict:
    return {
        "configId": "config-1",
        "project": "Master Data",
        "report": existing_report(),
        "sql": "SELECT 1 AS ERROREVALUATION FROM DUMMY",
        "changed": True,
        "validation": {"findings": []},
    }


def editor_model(message: str) -> dict:
    return {
        "version": 1,
        "report": existing_report(),
        "summary": {},
        "blocks": [],
        "source": {"attributes": []},
        "checks": {
            "groups": [
                {
                    "number": 1,
                    "title": "NAME",
                    "field": "NAME",
                    "description": "Name",
                    "rules": [
                        {
                            "condition": "NAME IS NULL",
                            "message": message,
                            "dimension": "Vollständigkeit",
                            "ruleType": "custom",
                            "active": True,
                        }
                    ],
                }
            ]
        },
        "output": {"fields": []},
        "validation": {"findings": []},
    }


def harmonization_report_model(report_id: str, internal_name: str, condition: str) -> dict:
    return {
        "report": {"id": report_id, "internalName": report_id, "displayName": report_id.title()},
        "model": {
            "report": {"id": report_id, "internalName": report_id, "displayName": report_id.title()},
            "source": {"attributes": [{"name": internal_name, "expression": internal_name, "comment": "Ort"}]},
            "checks": {
                "groups": [
                    {
                        "number": 1,
                        "title": f"{internal_name} (Ort)",
                        "displayName": "AddressCity",
                        "internalName": internal_name,
                        "field": internal_name,
                        "description": "Ort",
                        "rules": [
                            {
                                "condition": condition,
                                "message": "Ort fehlt",
                                "dimension": "Vollständigkeit",
                                "ruleType": "completeness",
                                "active": True,
                            }
                        ],
                    }
                ]
            },
            "blocks": [],
            "output": {"fields": []},
        },
    }


@contextmanager
def fake_nemo_context():
    yield SimpleNamespace(id="config-1"), object()


if __name__ == "__main__":
    unittest.main()
