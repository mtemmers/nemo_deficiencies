import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
SUPPORTED_AI_PROVIDERS = {
    "groq",
    "openai",
    "perplexity",
    "gemini",
    "ollama",
    "lmstudio",
    "openai_compatible",
}
CLOUD_AI_PROVIDERS = {"groq", "openai", "perplexity", "gemini"}
RULE_DIMENSIONS = [
    "Vollständigkeit",
    "Validität",
    "Korrektheit",
    "Eindeutigkeit",
    "Konsistenz",
    "Aktualität",
    "Genauigkeit",
    "Redundanz",
    "Einheitlichkeit",
    "Relevanz",
    "Zuverlässigkeit",
    "Verständlichkeit",
]
RULE_TYPES = [
    "completeness",
    "trim_whitespace",
    "min_length",
    "max_length",
    "regex",
    "obsolete_terms",
    "mixed_umlaut_spelling",
    "missing_letters",
    "legal_form_normalization",
    "custom",
]


class AIConnectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class AIConnectionSettings:
    provider: str
    base_url: str
    model: str
    api_key: str


class AIConnector(ABC):
    @abstractmethod
    def create_rule_draft(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def test_rule_examples(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def explain_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def revise_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def suggest_rules_from_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def translate_messages(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAICompatibleConnector(AIConnector):
    def __init__(self, settings: AIConnectionSettings, timeout: float = 45.0) -> None:
        self.settings = settings
        self.timeout = timeout

    def create_rule_draft(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        internal_name = str(payload.get("internalName") or "").strip()
        if not internal_name:
            raise AIConnectorError("Für den KI-Entwurf fehlt der Internalname des Feldes.")

        system = (
            "Du entwirfst Datenqualitätsregeln für SAP HANA SQL. Antworte ausschließlich im vorgegebenen JSON-Schema. "
            "Verwende in condition exakt den bereitgestellten Internalname als Feldbezeichner. "
            "Die condition enthält nur den booleschen Ausdruck nach WHEN, niemals WHEN, THEN, SQL-Kommentare oder Semikolon. "
            "Die message enthält keine führende Pipe. Erfinde keine zusätzlichen Felder. "
            "Beispiele sind fiktive Einzelwerte und enthalten keine echten Kunden- oder Geschäftsdaten. "
            + response_language_instruction(payload)
        )
        user = json.dumps(
            {
                "task": "Erzeuge genau einen prüfbaren Regelentwurf.",
                "field": {
                    "internalName": internal_name,
                    "displayName": payload.get("displayName") or "",
                    "description": payload.get("description") or "",
                    "dataType": payload.get("dataType") or "",
                },
                "businessRequirement": payload.get("requirement") or "",
                "existingRules": payload.get("existingRules") or [],
            },
            ensure_ascii=False,
        )
        result = self._complete_json(system, user, _rule_draft_schema())
        return validate_rule_draft(result, internal_name)

    def test_rule_examples(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        internal_name = str(payload.get("internalName") or "").strip()
        system = (
            "Du prüfst fachlich, ob ein Datenqualitäts-Regelentwurf die angegebenen Einzelwerte wie erwartet bewertet. "
            "Simuliere nur die Semantik des booleschen SAP-HANA-Ausdrucks und antworte ausschließlich im JSON-Schema. "
            "Kennzeichne Unsicherheit offen in explanation. " + response_language_instruction(payload)
        )
        user = json.dumps(
            {
                "field": internal_name,
                "condition": payload.get("condition") or "",
                "message": payload.get("message") or "",
                "examples": payload.get("examples") or [],
            },
            ensure_ascii=False,
        )
        return self._complete_json(system, user, _example_test_schema())

    def explain_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        internal_name = str(payload.get("internalName") or "").strip()
        condition = str(payload.get("condition") or "").strip()
        if not internal_name or not condition:
            raise AIConnectorError("Für die Formelerklärung fehlen Internalname oder Bedingung.")

        system = (
            "Du erklärst bestehende Datenqualitätsregeln in SAP HANA SQL für fachliche Anwender ohne SQL-Kenntnisse. "
            "Antworte ausschließlich im vorgegebenen JSON-Schema. Erkläre nur die vorhandene Bedingung und erfinde keine "
            "zusätzlichen Prüfungen. Beschreibe klar, wann die Bedingung TRUE wird und damit einen Datenqualitätsfehler auslöst. "
            "Prüfe Beispiele und Randfälle schrittweise gegen den booleschen Ausdruck. Gib bei jedem Randfall ausdrücklich an, "
            "ob die gesamte Bedingung TRUE oder FALSE ergibt. Nenne Unsicherheiten und SAP-HANA-Dialektbesonderheiten als "
            "Warnungen, statt sie als sichere Fakten darzustellen. Beispiele sind rein fiktiv. "
            + response_language_instruction(payload)
        )
        user = json.dumps(
            {
                "task": "Erkläre diese bestehende Datenqualitätsregel fachlich.",
                "field": {
                    "internalName": internal_name,
                    "displayName": payload.get("displayName") or "",
                    "description": payload.get("description") or "",
                    "dataType": payload.get("dataType") or "",
                },
                "rule": {
                    "condition": condition,
                    "message": payload.get("message") or "",
                    "dimension": payload.get("dimension") or "",
                    "ruleType": payload.get("ruleType") or "",
                },
            },
            ensure_ascii=False,
        )
        return self._complete_json(system, user, _rule_explanation_schema())

    def revise_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        internal_name = str(payload.get("internalName") or "").strip()
        condition = str(payload.get("condition") or "").strip()
        if not internal_name or not condition:
            raise AIConnectorError("Für die KI-Überarbeitung fehlen Internalname oder Bedingung.")

        system = (
            "Du prüfst und überarbeitest bestehende Datenqualitätsregeln in SAP HANA SQL. Antworte ausschließlich im "
            "vorgegebenen JSON-Schema. Die condition enthält nur den booleschen Ausdruck nach WHEN, niemals WHEN, THEN, "
            "SQL-Kommentare oder Semikolon. Bewahre alle Feldbezeichner aus der vorhandenen Bedingung exakt und führe "
            "keine weiteren Felder ein. Die message enthält keine führende Pipe. Ändere nur, was fachlich oder technisch "
            "begründet ist, und melde auch ausdrücklich, wenn keine Änderung erforderlich ist. Beispiele sind fiktiv. "
            + response_language_instruction(payload)
        )
        user = json.dumps(
            {
                "task": "Prüfe die bestehende Regel und liefere einen sicheren Verbesserungsvorschlag.",
                "field": {
                    "internalName": internal_name,
                    "displayName": payload.get("displayName") or "",
                    "description": payload.get("description") or "",
                    "dataType": payload.get("dataType") or "",
                },
                "currentRule": {
                    "condition": condition,
                    "message": payload.get("message") or "",
                    "dimension": payload.get("dimension") or "",
                    "ruleType": payload.get("ruleType") or "",
                },
                "userInstruction": payload.get("instruction") or "",
            },
            ensure_ascii=False,
        )
        result = self._complete_json(system, user, _rule_revision_schema())
        return validate_rule_revision(result, internal_name, condition)

    def suggest_rules_from_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        internal_name = str(payload.get("internalName") or "").strip()
        profile = payload.get("profile") or {}
        if not internal_name or not profile:
            raise AIConnectorError("Für KI-Regelvorschläge fehlen Feldname oder anonymisiertes Profil.")

        system = (
            "Du analysierst ein anonymisiertes Einspaltenprofil und schlägst Datenqualitätsregeln für SAP HANA SQL vor. "
            "Antworte ausschließlich im vorgegebenen JSON-Schema und liefere mindestens drei unterschiedliche Regeln. "
            "Wähle den fachlich passendsten DQ-Typ aus Vollständigkeit, Validität, Korrektheit, Eindeutigkeit, "
            "Konsistenz, Aktualität, Genauigkeit, Redundanz, Einheitlichkeit, Relevanz, Zuverlässigkeit und "
            "Verständlichkeit. Erfinde keine fachlichen "
            "Grenzwerte, erlaubten Wertelisten oder Zusammenhänge, die nicht durch Feldmetadaten oder Profil gestützt sind. "
            "Verwende in jeder condition exakt den Internalname als einzigen Feldbezeichner. Die condition enthält nur den "
            "booleschen Ausdruck nach WHEN, niemals WHEN, THEN, SQL-Kommentare oder Semikolon. Jede message enthält keine "
            "führende Pipe. Erkläre in evidence, welches anonymisierte Muster den Vorschlag stützt. Verwende für reguläre "
            "Ausdrücke ausschließlich die SAP-HANA-Syntax FIELD LIKE_REGEXPR 'pattern' beziehungsweise FIELD NOT "
            "LIKE_REGEXPR 'pattern', niemals REGEXP. Wende TRIM, LENGTH oder Regex nur auf textuelle Datentypen an. Für "
            "date oder timestamp sind ausschließlich NULL-Prüfungen, Datumsvergleiche, CURRENT_DATE und passende "
            "SAP-HANA-Datumsfunktionen erlaubt. Für numerische Datentypen sind keine Textfunktionen erlaubt. "
            + response_language_instruction(payload)
        )
        user = json.dumps(
            {
                "task": "Erzeuge mindestens drei auswählbare Datenqualitätsregeln aus dem Feldprofil.",
                "field": {
                    "internalName": internal_name,
                    "displayName": payload.get("displayName") or "",
                    "description": payload.get("description") or "",
                    "dataType": payload.get("dataType") or "",
                },
                "anonymizedProfile": profile,
            },
            ensure_ascii=False,
        )
        result = self._complete_json(system, user, _field_rule_suggestion_schema())
        data_type = str(payload.get("dataType") or "")
        try:
            return validate_field_rule_suggestions(result, internal_name, data_type)
        except AIConnectorError as exc:
            correction = json.dumps(
                {
                    "task": "Korrigiere die vorige Antwort und liefere mindestens drei gültige Regelvorschläge.",
                    "validationError": str(exc),
                    "field": {
                        "internalName": internal_name,
                        "dataType": data_type,
                    },
                    "previousResponse": result,
                    "anonymizedProfile": profile,
                },
                ensure_ascii=False,
            )
            corrected = self._complete_json(
                system + " Die vorige Antwort war ungültig. Behebe exakt den genannten Validierungsfehler.",
                correction,
                _field_rule_suggestion_schema(),
            )
            return validate_field_rule_suggestions(corrected, internal_name, data_type)

    def translate_messages(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_language = normalize_language(payload.get("targetLanguage"))
        messages = list(payload.get("messages") or [])
        translated: list[Dict[str, str]] = []
        for start in range(0, len(messages), 40):
            chunk = messages[start : start + 40]
            system = (
                "Du übersetzt ausschließlich fachliche Fehlermeldungen von Datenqualitätsregeln. "
                f"Zielsprache: {language_name(target_language)}. Bewahre Bedeutung, Feldbezeichnungen, Zahlen, "
                "Abkürzungen und Platzhalter exakt. Ergänze keine führende Pipe, keine SQL-Syntax und keine Erklärung. "
                "Gib jede empfangene id genau einmal und in derselben Reihenfolge zurück."
            )
            user = json.dumps({"messages": chunk}, ensure_ascii=False)
            result = self._complete_json(system, user, _message_translation_schema())
            translated.extend(validate_message_translations(result, chunk))
        return {"targetLanguage": target_language, "translations": translated}

    def test_connection(self) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {"status": {"type": "string", "enum": ["ok"]}},
            "required": ["status"],
            "additionalProperties": False,
        }
        result = self._complete_json("Antworte mit dem vorgegebenen JSON.", "Verbindungstest", schema)
        return {"status": result.get("status"), "model": self.settings.model}

    def _complete_json(self, system: str, user: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_instruction = (
            "\nAntworte als einzelnes JSON-Objekt, das exakt diesem JSON-Schema entspricht:\n"
            + json.dumps(schema, ensure_ascii=False)
        )
        body = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system + schema_instruction},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "nemo_rule_response", "strict": True, "schema": schema},
            },
        }
        response = self._post_completion(body)
        if not response.ok and response.status_code in {400, 415, 422}:
            fallback_body = dict(body)
            fallback_body["response_format"] = {"type": "json_object"}
            response = self._post_completion(fallback_body)
        if not response.ok and response.status_code in {400, 415, 422}:
            fallback_body = dict(body)
            fallback_body.pop("response_format", None)
            response = self._post_completion(fallback_body)
        if not response.ok:
            self._raise_response_error(response)

        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise AIConnectorError("Der KI-Dienst hat keine lesbare Antwort geliefert.") from exc

        try:
            content = payload["choices"][0]["message"]["content"]
            if isinstance(content, dict):
                return content
            if isinstance(content, list):
                content = "".join(str(part.get("text") or "") for part in content if isinstance(part, dict))
            return json.loads(strip_json_fence(str(content)))
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AIConnectorError("Die strukturierte KI-Antwort ist unvollständig.") from exc

    def _post_completion(self, body: Dict[str, Any]):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "nemo-deficiencies/0.2",
        }
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        base_url = self.settings.base_url.rstrip("/")
        endpoint = base_url if base_url.casefold().endswith("/chat/completions") else f"{base_url}/chat/completions"
        for attempt in range(3):
            try:
                response = requests.post(endpoint, json=body, headers=headers, timeout=self.timeout)
            except requests.Timeout as exc:
                raise AIConnectorError(
                    "Das KI-Modell hat nicht rechtzeitig geantwortet. Bereits übersetzte Pakete bleiben erhalten. "
                    "Bitte erneut versuchen oder ein schnelleres KI-Modell wählen."
                ) from exc
            except requests.ConnectionError as exc:
                raise AIConnectorError("Der KI-Dienst ist momentan nicht erreichbar. Bitte Verbindung und API-Adresse prüfen.") from exc
            except requests.RequestException as exc:
                raise AIConnectorError(f"Der KI-Aufruf ist fehlgeschlagen: {exc}") from exc
            if response.status_code not in {502, 503, 504} or attempt == 2:
                return response
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = min(max(float(retry_after), 0.5), 5.0)
            except (TypeError, ValueError):
                delay = 1.0 + attempt
            time.sleep(delay)
        return response

    def _raise_response_error(self, response) -> None:
        detail = response.text.strip()[:1000] or response.reason
        error_code = ""
        try:
            error = (response.json() or {}).get("error") or {}
            error_code = str(error.get("code") or error.get("type") or "").casefold()
        except (ValueError, AttributeError, TypeError):
            pass
        if response.status_code == 429 and error_code == "insufficient_quota":
            raise AIConnectorError(
                "Das API-Kontingent dieses OpenAI-Kontos ist aufgebraucht oder die API-Abrechnung ist nicht eingerichtet. "
                "Bitte Guthaben, Zahlungsart und Nutzungslimit in der OpenAI Platform prüfen."
            )
        if response.status_code == 429:
            raise AIConnectorError(
                "Der KI-Dienst hat sein aktuelles Anfrage- oder Nutzungslimit erreicht. Bitte kurz warten oder das Limit prüfen."
            )
        if response.status_code in {502, 503, 504}:
            raise AIConnectorError(
                "Das ausgewählte KI-Modell ist momentan überlastet oder vorübergehend nicht verfügbar. "
                "Die Anfrage wurde automatisch dreimal versucht. Bitte kurz warten, erneut ausführen oder ein anderes KI-Profil wählen."
            )
        if response.status_code == 403 and "1010" in detail and self.settings.provider == "groq":
            raise AIConnectorError(
                "Groq hat die Signatur des HTTP-Clients abgewiesen (Cloudflare 1010). "
                "Bitte den Server mit dem aktualisierten Client neu starten und erneut versuchen."
            )
        raise AIConnectorError(f"Der KI-Dienst hat die Anfrage abgelehnt ({response.status_code}): {detail}")


def create_ai_connector(settings: AIConnectionSettings) -> AIConnector:
    provider = settings.provider.strip().casefold()
    if provider in CLOUD_AI_PROVIDERS and not settings.api_key.strip():
        raise AIConnectorError("Für diesen Cloud-Anbieter ist ein API-Key erforderlich.")
    if provider in SUPPORTED_AI_PROVIDERS:
        return OpenAICompatibleConnector(settings)
    raise AIConnectorError(f"Nicht unterstützter KI-Anbieter: {settings.provider}")


def strip_json_fence(content: str) -> str:
    clean = content.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", clean, re.I | re.S)
    return match.group(1).strip() if match else clean


def normalize_language(value: Any) -> str:
    language = str(value or "de").strip().casefold()
    return language if language in {"de", "en"} else "de"


def language_name(language: str) -> str:
    return "Englisch" if normalize_language(language) == "en" else "Deutsch"


def response_language_instruction(payload: Dict[str, Any]) -> str:
    return f"Formuliere alle fachlichen Texte und Fehlermeldungen auf {language_name(payload.get('language'))}."


def validate_message_translations(result: Dict[str, Any], source: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    translations = list(result.get("translations") or [])
    expected_ids = [str(item.get("id") or "") for item in source]
    actual_ids = [str(item.get("id") or "") for item in translations]
    if actual_ids != expected_ids:
        raise AIConnectorError("Die KI-Übersetzung hat Regel-IDs ausgelassen oder verändert.")
    cleaned: list[Dict[str, str]] = []
    for item in translations:
        text = str(item.get("text") or "").strip().lstrip("|").strip()
        if not text:
            raise AIConnectorError("Die KI-Übersetzung enthält eine leere Fehlermeldung.")
        cleaned.append({"id": str(item.get("id") or ""), "text": text})
    return cleaned


def validate_rule_draft(draft: Dict[str, Any], internal_name: str) -> Dict[str, Any]:
    condition = str(draft.get("condition") or "").strip()
    message = str(draft.get("message") or "").strip().lstrip("|").strip()
    if not condition or not message:
        raise AIConnectorError("Der KI-Regelentwurf enthält keine vollständige Bedingung und Fehlermeldung.")
    identifier_pattern = rf"(?<![A-Za-z0-9_]){re.escape(internal_name)}(?![A-Za-z0-9_])"
    if not re.search(identifier_pattern, condition, re.I):
        raise AIConnectorError("Der KI-Regelentwurf verwendet nicht den Internalname des ausgewählten Feldes.")
    if ";" in condition or re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|GRANT|REVOKE)\b", condition, re.I):
        raise AIConnectorError("Der KI-Regelentwurf enthält eine nicht erlaubte SQL-Anweisung.")
    if re.search(r"\b(WHEN|THEN)\b", condition, re.I):
        raise AIConnectorError("Die KI-Bedingung darf nur den Ausdruck nach WHEN enthalten.")
    draft["condition"] = condition
    draft["message"] = message
    draft["examples"] = list(draft.get("examples") or [])[:8]
    return draft


def validate_rule_revision(
    revision: Dict[str, Any], internal_name: str, original_condition: str
) -> Dict[str, Any]:
    condition = str(revision.get("condition") or "").strip()
    message = str(revision.get("message") or "").strip().lstrip("|").strip()
    if not condition or not message:
        raise AIConnectorError("Der KI-Vorschlag enthält keine vollständige Bedingung und Fehlermeldung.")
    if ";" in condition or re.search(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|GRANT|REVOKE)\b", condition, re.I
    ):
        raise AIConnectorError("Der KI-Vorschlag enthält eine nicht erlaubte SQL-Anweisung.")
    if re.search(r"\b(WHEN|THEN)\b", condition, re.I):
        raise AIConnectorError("Die KI-Bedingung darf nur den Ausdruck nach WHEN enthalten.")

    original_identifiers = _condition_identifiers(original_condition)
    proposed_identifiers = _condition_identifiers(condition)
    if not original_identifiers:
        original_identifiers = {internal_name.casefold()}
    introduced = proposed_identifiers - original_identifiers
    if introduced:
        names = ", ".join(sorted(introduced))
        raise AIConnectorError(f"Der KI-Vorschlag führt unbekannte Feldbezeichner ein: {names}.")
    if not (proposed_identifiers & original_identifiers):
        raise AIConnectorError("Der KI-Vorschlag verwendet keinen Feldbezeichner der bestehenden Bedingung.")

    revision["condition"] = condition
    revision["message"] = message
    revision["changes"] = list(revision.get("changes") or [])[:12]
    revision["warnings"] = list(revision.get("warnings") or [])[:12]
    revision["examples"] = list(revision.get("examples") or [])[:8]
    return revision


def validate_field_rule_suggestions(
    result: Dict[str, Any], internal_name: str, data_type: str = ""
) -> Dict[str, Any]:
    suggestions = list(result.get("suggestions") or [])
    if len(suggestions) < 3:
        raise AIConnectorError("Die KI hat weniger als drei Regelvorschläge geliefert.")
    validated = []
    seen_conditions = set()
    for suggestion in suggestions[:8]:
        draft = validate_rule_draft(dict(suggestion), internal_name)
        _validate_profile_condition_for_type(draft["condition"], data_type)
        condition_key = draft["condition"].casefold()
        if condition_key in seen_conditions:
            continue
        seen_conditions.add(condition_key)
        validated.append(draft)
    if len(validated) < 3:
        raise AIConnectorError("Die KI hat weniger als drei unterschiedliche Regelvorschläge geliefert.")
    result["suggestions"] = validated
    return result


def _validate_profile_condition_for_type(condition: str, data_type: str) -> None:
    if re.search(r"(?<!LIKE_)\bREGEXP\b", condition, re.I):
        raise AIConnectorError("Ein KI-Vorschlag verwendet nicht die SAP-HANA-Syntax LIKE_REGEXPR.")
    normalized_type = str(data_type or "").casefold()
    text_functions = r"\b(TRIM|LENGTH|LIKE_REGEXPR|REGEXP)\b"
    if any(token in normalized_type for token in ("date", "time")) and re.search(text_functions, condition, re.I):
        raise AIConnectorError("Ein KI-Vorschlag verwendet Textfunktionen auf einem Datumsfeld.")
    if any(token in normalized_type for token in ("int", "decimal", "double", "numeric", "number")) and re.search(
        text_functions, condition, re.I
    ):
        raise AIConnectorError("Ein KI-Vorschlag verwendet Textfunktionen auf einem numerischen Feld.")


def _condition_identifiers(condition: str) -> set[str]:
    without_literals = re.sub(r"'(?:''|[^'])*'", " ", str(condition or ""))
    ignored = {
        "and", "or", "not", "is", "null", "true", "false", "like", "in", "between", "escape",
        "case", "when", "then", "else", "end", "as", "distinct", "from", "where", "select",
        "integer", "bigint", "decimal", "double", "date", "timestamp", "nvarchar", "varchar",
        "like_regexpr", "occurrences_regexpr", "locate_regexpr", "match",
    }
    identifiers: set[str] = set()
    for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", without_literals):
        token = match.group(0).casefold()
        if token in ignored:
            continue
        remainder = without_literals[match.end():]
        if re.match(r"\s*\(", remainder):
            continue
        identifiers.add(token)
    return identifiers


def _rule_draft_schema() -> Dict[str, Any]:
    example = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "expectedViolation": {"type": "boolean"},
            "explanation": {"type": "string"},
        },
        "required": ["value", "expectedViolation", "explanation"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "ruleType": {"type": "string", "enum": RULE_TYPES},
            "dimension": {"type": "string", "enum": RULE_DIMENSIONS},
            "condition": {"type": "string"},
            "message": {"type": "string"},
            "rationale": {"type": "string"},
            "clarificationQuestion": {"type": ["string", "null"]},
            "examples": {"type": "array", "items": example},
        },
        "required": [
            "ruleType",
            "dimension",
            "condition",
            "message",
            "rationale",
            "clarificationQuestion",
            "examples",
        ],
        "additionalProperties": False,
    }


def _example_test_schema() -> Dict[str, Any]:
    result = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "expectedViolation": {"type": "boolean"},
            "actualViolation": {"type": "boolean"},
            "matchesExpectation": {"type": "boolean"},
            "explanation": {"type": "string"},
        },
        "required": ["value", "expectedViolation", "actualViolation", "matchesExpectation", "explanation"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "allPassed": {"type": "boolean"},
            "results": {"type": "array", "items": result},
            "summary": {"type": "string"},
        },
        "required": ["allPassed", "results", "summary"],
        "additionalProperties": False,
    }


def _rule_explanation_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "triggerBehavior": {"type": "string"},
            "validExamples": {"type": "array", "items": {"type": "string"}},
            "invalidExamples": {"type": "array", "items": {"type": "string"}},
            "edgeCases": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "summary",
            "triggerBehavior",
            "validExamples",
            "invalidExamples",
            "edgeCases",
            "warnings",
        ],
        "additionalProperties": False,
    }


def _rule_revision_schema() -> Dict[str, Any]:
    example = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "expectedViolation": {"type": "boolean"},
            "explanation": {"type": "string"},
        },
        "required": ["value", "expectedViolation", "explanation"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "hasChanges": {"type": "boolean"},
            "condition": {"type": "string"},
            "message": {"type": "string"},
            "dimension": {"type": "string", "enum": RULE_DIMENSIONS},
            "ruleType": {"type": "string", "enum": RULE_TYPES},
            "assessment": {"type": "string"},
            "changes": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "clarificationQuestion": {"type": ["string", "null"]},
            "examples": {"type": "array", "items": example},
        },
        "required": [
            "hasChanges", "condition", "message", "dimension", "ruleType", "assessment", "changes",
            "warnings", "clarificationQuestion", "examples",
        ],
        "additionalProperties": False,
    }


def _field_rule_suggestion_schema() -> Dict[str, Any]:
    example = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "expectedViolation": {"type": "boolean"},
            "explanation": {"type": "string"},
        },
        "required": ["value", "expectedViolation", "explanation"],
        "additionalProperties": False,
    }
    suggestion = {
        "type": "object",
        "properties": {
            "ruleType": {"type": "string", "enum": RULE_TYPES},
            "dimension": {"type": "string", "enum": RULE_DIMENSIONS},
            "condition": {"type": "string"},
            "message": {"type": "string"},
            "rationale": {"type": "string"},
            "evidence": {"type": "string"},
            "examples": {"type": "array", "items": example},
        },
        "required": ["ruleType", "dimension", "condition", "message", "rationale", "evidence", "examples"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "profileSummary": {"type": "string"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "suggestions": {"type": "array", "items": suggestion, "minItems": 3, "maxItems": 8},
        },
        "required": ["profileSummary", "warnings", "suggestions"],
        "additionalProperties": False,
    }


def _message_translation_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}, "text": {"type": "string"}},
                    "required": ["id", "text"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["translations"],
        "additionalProperties": False,
    }
