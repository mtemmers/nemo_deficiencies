import json
import unittest
from unittest.mock import Mock, patch

import requests

from backend.services.ai_connector import (
    AIConnectionSettings,
    AIConnectorError,
    OpenAICompatibleConnector,
    create_ai_connector,
    strip_json_fence,
    validate_rule_draft,
    validate_rule_revision,
    validate_field_rule_suggestions,
)


class AIConnectorTest(unittest.TestCase):
    def test_all_configurable_providers_use_the_compatible_connector(self) -> None:
        for provider in ("groq", "openai", "gemini", "perplexity", "ollama", "lmstudio", "openai_compatible"):
            api_key = "key" if provider in {"groq", "openai", "gemini", "perplexity"} else ""
            connector = create_ai_connector(AIConnectionSettings(provider, "http://localhost:11434/v1", "model", api_key))
            self.assertIsInstance(connector, OpenAICompatibleConnector)

    def test_cloud_provider_requires_api_key(self) -> None:
        with self.assertRaises(AIConnectorError):
            create_ai_connector(AIConnectionSettings("openai", "https://api.openai.com/v1", "model", ""))

    def test_local_provider_omits_authorization_header(self) -> None:
        response = Mock(ok=True)
        response.json.return_value = {"choices": [{"message": {"content": '{"status":"ok"}'}}]}
        connector = create_ai_connector(
            AIConnectionSettings("ollama", "http://localhost:11434/v1", "qwen3:8b", "")
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response) as post:
            connector.test_connection()

        self.assertNotIn("Authorization", post.call_args.kwargs["headers"])
        self.assertEqual("http://localhost:11434/v1/chat/completions", post.call_args.args[0])

    def test_rule_messages_are_translated_with_stable_ids(self) -> None:
        response = Mock(ok=True)
        response.json.return_value = {
            "choices": [{"message": {"content": json.dumps({
                "translations": [{"id": "rule-1", "text": "Customer number is missing"}],
            })}}]
        }
        connector = create_ai_connector(
            AIConnectionSettings("groq", "https://api.groq.com/openai/v1", "model", "key")
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response):
            result = connector.translate_messages({
                "targetLanguage": "en",
                "messages": [{"id": "rule-1", "text": "Kundennummer fehlt"}],
            })

        self.assertEqual("en", result["targetLanguage"])
        self.assertEqual("Customer number is missing", result["translations"][0]["text"])

    def test_unsupported_json_schema_falls_back_to_json_object(self) -> None:
        rejected = Mock(ok=False, status_code=400, text="unsupported response_format", reason="Bad Request")
        accepted = Mock(ok=True)
        accepted.json.return_value = {"choices": [{"message": {"content": "```json\n{\"status\":\"ok\"}\n```"}}]}
        connector = create_ai_connector(
            AIConnectionSettings("lmstudio", "http://localhost:1234/v1", "local-model", "")
        )

        with patch("backend.services.ai_connector.requests.post", side_effect=[rejected, accepted]) as post:
            result = connector.test_connection()

        self.assertEqual("ok", result["status"])
        self.assertEqual({"type": "json_object"}, post.call_args_list[1].kwargs["json"]["response_format"])
        self.assertEqual('{"status":"ok"}', strip_json_fence("```json\n{\"status\":\"ok\"}\n```"))

    def test_openai_quota_error_is_explained_without_raw_json(self) -> None:
        response = Mock(ok=False, status_code=429, text='{"error":{"code":"insufficient_quota"}}', reason="Too Many Requests")
        response.json.return_value = {"error": {"code": "insufficient_quota"}}
        connector = create_ai_connector(
            AIConnectionSettings("openai", "https://api.openai.com/v1", "gpt-5-mini", "key")
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response):
            with self.assertRaisesRegex(AIConnectorError, "API-Kontingent") as raised:
                connector.test_connection()

        self.assertNotIn("insufficient_quota", str(raised.exception))

    def test_temporarily_unavailable_model_is_retried(self) -> None:
        unavailable = Mock(ok=False, status_code=503, text='{"error":{"status":"UNAVAILABLE"}}', reason="Unavailable")
        unavailable.headers = {}
        accepted = Mock(ok=True, status_code=200)
        accepted.json.return_value = {"choices": [{"message": {"content": '{"status":"ok"}'}}]}
        connector = create_ai_connector(
            AIConnectionSettings("gemini", "https://example.test/v1", "model", "key")
        )

        with patch("backend.services.ai_connector.requests.post", side_effect=[unavailable, accepted]) as post, patch(
            "backend.services.ai_connector.time.sleep"
        ):
            result = connector.test_connection()

        self.assertEqual("ok", result["status"])
        self.assertEqual(2, post.call_count)

    def test_persistent_model_overload_has_readable_error(self) -> None:
        unavailable = Mock(ok=False, status_code=503, text='{"error":{"message":"high demand"}}', reason="Unavailable")
        unavailable.headers = {}
        connector = create_ai_connector(
            AIConnectionSettings("gemini", "https://example.test/v1", "model", "key")
        )

        with patch("backend.services.ai_connector.requests.post", return_value=unavailable), patch(
            "backend.services.ai_connector.time.sleep"
        ), self.assertRaisesRegex(AIConnectorError, "automatisch dreimal") as raised:
            connector.test_connection()

        self.assertNotIn("high demand", str(raised.exception))

    def test_timeout_has_readable_error_without_connection_details(self) -> None:
        connector = create_ai_connector(
            AIConnectionSettings("gemini", "https://example.test/v1", "model", "key")
        )

        with patch("backend.services.ai_connector.requests.post", side_effect=requests.Timeout("raw timeout")):
            with self.assertRaisesRegex(AIConnectorError, "nicht rechtzeitig") as raised:
                connector.test_connection()

        self.assertNotIn("raw timeout", str(raised.exception))

    def test_field_profile_requires_three_distinct_safe_suggestions(self) -> None:
        suggestions = []
        for index, condition in enumerate(
            ["CUSTOMER_ID IS NULL", "TRIM(CUSTOMER_ID) = ''", "LENGTH(CUSTOMER_ID) < 3"]
        ):
            suggestions.append(
                {
                    "condition": condition,
                    "message": f"Regel {index}",
                    "dimension": "Korrektheit",
                    "ruleType": "custom",
                    "examples": [],
                }
            )

        result = validate_field_rule_suggestions({"suggestions": suggestions}, "CUSTOMER_ID")

        self.assertEqual(3, len(result["suggestions"]))

    def test_field_profile_rejects_fewer_than_three_suggestions(self) -> None:
        with self.assertRaises(AIConnectorError):
            validate_field_rule_suggestions(
                {
                    "suggestions": [
                        {
                            "condition": "CUSTOMER_ID IS NULL",
                            "message": "Fehlt",
                            "examples": [],
                        }
                    ]
                },
                "CUSTOMER_ID",
            )

    def test_field_profile_rejects_text_rules_for_date_field(self) -> None:
        suggestions = [
            {
                "condition": condition,
                "message": f"Regel {index}",
                "examples": [],
            }
            for index, condition in enumerate(
                ["CHANGE_DATE IS NULL", "LENGTH(CHANGE_DATE) < 10", "CHANGE_DATE > CURRENT_DATE"]
            )
        ]

        with self.assertRaises(AIConnectorError):
            validate_field_rule_suggestions({"suggestions": suggestions}, "CHANGE_DATE", "date")

    def test_field_profile_retries_once_after_invalid_typed_suggestion(self) -> None:
        connector = OpenAICompatibleConnector(
            AIConnectionSettings("groq", "https://api.groq.com/openai/v1", "model", "key")
        )

        def suggestion(condition: str, index: int) -> dict:
            return {
                "condition": condition,
                "message": f"Regel {index}",
                "dimension": "Korrektheit",
                "ruleType": "custom",
                "examples": [],
            }

        invalid = {
            "suggestions": [
                suggestion("CHANGE_DATE IS NULL", 1),
                suggestion("LENGTH(CHANGE_DATE) < 10", 2),
                suggestion("CHANGE_DATE > CURRENT_DATE", 3),
            ]
        }
        corrected = {
            "suggestions": [
                suggestion("CHANGE_DATE IS NULL", 1),
                suggestion("CHANGE_DATE > CURRENT_DATE", 2),
                suggestion("CHANGE_DATE < ADD_YEARS(CURRENT_DATE, -20)", 3),
            ]
        }

        with patch.object(connector, "_complete_json", side_effect=[invalid, corrected]) as complete:
            result = connector.suggest_rules_from_profile(
                {
                    "internalName": "CHANGE_DATE",
                    "dataType": "date",
                    "profile": {"sampleSize": 20},
                }
            )

        self.assertEqual(2, complete.call_count)
        self.assertEqual(3, len(result["suggestions"]))

    def test_rule_draft_keeps_internal_name_and_removes_message_pipe(self) -> None:
        draft = validate_rule_draft(
            {
                "condition": "CUSTOMER_ID IS NULL",
                "message": "|Kundennummer fehlt",
                "examples": [],
            },
            "CUSTOMER_ID",
        )

        self.assertEqual("CUSTOMER_ID IS NULL", draft["condition"])
        self.assertEqual("Kundennummer fehlt", draft["message"])

    def test_rule_draft_rejects_other_field(self) -> None:
        with self.assertRaises(AIConnectorError):
            validate_rule_draft(
                {"condition": "OTHER_FIELD IS NULL", "message": "Fehlt", "examples": []},
                "CUSTOMER_ID",
            )

    def test_rule_draft_rejects_sql_statements(self) -> None:
        with self.assertRaises(AIConnectorError):
            validate_rule_draft(
                {"condition": "CUSTOMER_ID IS NULL; DELETE FROM X", "message": "Fehlt", "examples": []},
                "CUSTOMER_ID",
            )

    def test_api_request_uses_named_client_signature(self) -> None:
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "choices": [{"message": {"content": '{"status":"ok"}'}}]
        }
        connector = OpenAICompatibleConnector(
            AIConnectionSettings(
                provider="groq",
                base_url="https://api.groq.com/openai/v1",
                model="openai/gpt-oss-120b",
                api_key="gsk-test",
            )
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response) as post:
            result = connector.test_connection()

        self.assertEqual("ok", result["status"])
        headers = post.call_args.kwargs["headers"]
        self.assertEqual("nemo-deficiencies/0.2", headers["User-Agent"])
        self.assertEqual("application/json", headers["Accept"])

    def test_existing_rule_can_be_explained_structurally(self) -> None:
        explanation = {
            "summary": "Prüft auf einen leeren Wert.",
            "triggerBehavior": "Ein Fehler entsteht bei NULL.",
            "validExamples": ["C100"],
            "invalidExamples": ["NULL"],
            "edgeCases": ["Leerzeichen werden nicht geprüft."],
            "warnings": [],
        }
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(explanation)}}]
        }
        connector = OpenAICompatibleConnector(
            AIConnectionSettings(
                provider="groq",
                base_url="https://api.groq.com/openai/v1",
                model="openai/gpt-oss-120b",
                api_key="gsk-test",
            )
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response):
            result = connector.explain_rule(
                {
                    "internalName": "CUSTOMER_ID",
                    "condition": "CUSTOMER_ID IS NULL",
                    "message": "Kundennummer fehlt",
                }
            )

        self.assertEqual(explanation, result)

    def test_existing_rule_can_be_revised_without_changing_its_field(self) -> None:
        revision = {
            "hasChanges": True,
            "condition": "FULLNAME_I IS NULL OR TRIM(FULLNAME_I) = ''",
            "message": "|Kundenbezeichnung fehlt",
            "dimension": "Vollständigkeit",
            "ruleType": "completeness",
            "assessment": "Leerzeichen sollten ebenfalls als leer gelten.",
            "changes": ["TRIM ergänzt"],
            "warnings": [],
            "clarificationQuestion": None,
            "examples": [],
        }

        result = validate_rule_revision(
            revision,
            internal_name="address_name",
            original_condition="FULLNAME_I IS NULL OR FULLNAME_I = ''",
        )

        self.assertEqual("FULLNAME_I IS NULL OR TRIM(FULLNAME_I) = ''", result["condition"])
        self.assertEqual("Kundenbezeichnung fehlt", result["message"])

    def test_rule_revision_rejects_a_new_field_identifier(self) -> None:
        with self.assertRaises(AIConnectorError):
            validate_rule_revision(
                {
                    "condition": "CUSTOMER_ID IS NULL OR OTHER_FIELD IS NULL",
                    "message": "Kundennummer fehlt",
                },
                internal_name="CUSTOMER_ID",
                original_condition="CUSTOMER_ID IS NULL",
            )

    def test_rule_revision_uses_structured_ai_response(self) -> None:
        revision = {
            "hasChanges": False,
            "condition": "CUSTOMER_ID IS NULL",
            "message": "Kundennummer fehlt",
            "dimension": "Vollständigkeit",
            "ruleType": "completeness",
            "assessment": "Die Regel ist korrekt.",
            "changes": [],
            "warnings": [],
            "clarificationQuestion": None,
            "examples": [],
        }
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(revision)}}]
        }
        connector = OpenAICompatibleConnector(
            AIConnectionSettings(
                provider="groq",
                base_url="https://api.groq.com/openai/v1",
                model="openai/gpt-oss-120b",
                api_key="gsk-test",
            )
        )

        with patch("backend.services.ai_connector.requests.post", return_value=response):
            result = connector.revise_rule(
                {
                    "internalName": "CUSTOMER_ID",
                    "condition": "CUSTOMER_ID IS NULL",
                    "message": "Kundennummer fehlt",
                }
            )

        self.assertFalse(result["hasChanges"])
        self.assertEqual("CUSTOMER_ID IS NULL", result["condition"])


if __name__ == "__main__":
    unittest.main()
