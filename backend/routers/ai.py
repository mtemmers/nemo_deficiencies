from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["ai"])


class AIConfigCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(default="Groq", min_length=1, max_length=120)
    provider: str = Field(
        default="groq",
        pattern=r"^(groq|openai|perplexity|gemini|ollama|lmstudio|openai_compatible|litellm)$",
    )
    base_url: str = Field(default="https://api.groq.com/openai/v1", alias="baseUrl", min_length=1, max_length=500)
    model: str = Field(default="openai/gpt-oss-120b", min_length=1, max_length=200)
    api_key: str = Field(default="", alias="apiKey", max_length=2048)


class AIRuleDraftRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    ai_config_id: Optional[str] = Field(default=None, alias="aiConfigId")
    internal_name: str = Field(alias="internalName", min_length=1, max_length=240)
    display_name: str = Field(default="", alias="displayName", max_length=500)
    description: str = Field(default="", max_length=2000)
    data_type: str = Field(default="", alias="dataType", max_length=120)
    requirement: str = Field(min_length=3, max_length=4000)
    existing_rules: list[dict] = Field(default_factory=list, alias="existingRules", max_length=100)
    language: str = Field(default="de", pattern=r"^(de|en)$")


class AIRuleExampleTestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    ai_config_id: Optional[str] = Field(default=None, alias="aiConfigId")
    internal_name: str = Field(alias="internalName", min_length=1, max_length=240)
    condition: str = Field(min_length=1, max_length=100_000)
    message: str = Field(default="", max_length=1000)
    examples: list[dict] = Field(min_length=1, max_length=20)
    language: str = Field(default="de", pattern=r"^(de|en)$")


class AIRuleExplanationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    ai_config_id: Optional[str] = Field(default=None, alias="aiConfigId")
    internal_name: str = Field(alias="internalName", min_length=1, max_length=240)
    display_name: str = Field(default="", alias="displayName", max_length=500)
    description: str = Field(default="", max_length=2000)
    data_type: str = Field(default="", alias="dataType", max_length=120)
    condition: str = Field(min_length=1, max_length=100_000)
    message: str = Field(default="", max_length=1000)
    dimension: str = Field(default="", max_length=120)
    rule_type: str = Field(default="", alias="ruleType", max_length=120)
    language: str = Field(default="de", pattern=r"^(de|en)$")


class AIRuleRevisionRequest(AIRuleExplanationRequest):
    instruction: str = Field(default="", max_length=4000)


class AIFieldRuleSuggestionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    ai_config_id: Optional[str] = Field(default=None, alias="aiConfigId")
    project: str = Field(default="Master Data", min_length=1, max_length=120)
    internal_name: str = Field(alias="internalName", min_length=1, max_length=240)
    display_name: str = Field(default="", alias="displayName", max_length=500)
    description: str = Field(default="", max_length=2000)
    data_type: str = Field(default="", alias="dataType", max_length=120)
    max_rows: int = Field(default=500, alias="maxRows", ge=50, le=1000)
    language: str = Field(default="de", pattern=r"^(de|en)$")


class AIMessageTranslationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    ai_config_id: Optional[str] = Field(default=None, alias="aiConfigId")
    target_language: str = Field(alias="targetLanguage", pattern=r"^(de|en)$")
    messages: list[dict] = Field(min_length=1, max_length=500)


@router.get("/api/ai/configs")
def list_ai_configs() -> dict:
    from backend import main as m

    profiles = m._ai_store().list_profiles()
    return {
        "configs": [profile.to_dict() for profile in profiles],
        "defaultAiConfigId": profiles[0].id if profiles else None,
    }


@router.post("/api/ai/configs", status_code=201)
def create_ai_config(request: AIConfigCreateRequest) -> dict:
    from backend import main as m

    try:
        connector = m.create_ai_connector(
            m.AIConnectionSettings(
                provider=request.provider,
                base_url=request.base_url,
                model=request.model,
                api_key=request.api_key,
            )
        )
        connector.test_connection()
        profile = m._ai_store().create_profile(
            name=request.name,
            provider=request.provider,
            base_url=request.base_url,
            model=request.model,
            api_key=request.api_key,
        )
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except m.AIConfigStoreError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    m.log.info("KI-Konfiguration angelegt: id=%s provider=%s model=%s", profile.id, profile.provider, profile.model)
    return {"config": profile.to_dict()}


@router.post("/api/ai/configs/{ai_config_id}/test")
def test_ai_config(ai_config_id: str) -> dict:
    from backend import main as m

    try:
        connector = m.create_ai_connector(m._ai_store().resolve_settings(ai_config_id))
        return connector.test_connection()
    except m.AIConfigNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except m.AIConfigStoreError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/api/ai/rules/draft")
def create_ai_rule_draft(request: AIRuleDraftRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        draft = connector.create_rule_draft(request.model_dump(by_alias=True))
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "draft": draft}


@router.post("/api/ai/rules/test-examples")
def test_ai_rule_examples(request: AIRuleExampleTestRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        result = connector.test_rule_examples(request.model_dump(by_alias=True))
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "test": result, "testType": "semantic-ai-review"}


@router.post("/api/ai/rules/explain")
def explain_ai_rule(request: AIRuleExplanationRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        explanation = connector.explain_rule(request.model_dump(by_alias=True))
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "explanation": explanation}


@router.post("/api/ai/rules/revise")
def revise_ai_rule(request: AIRuleRevisionRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        revision = connector.revise_rule(request.model_dump(by_alias=True))
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "revision": revision}


@router.post("/api/ai/messages/translate")
def translate_ai_messages(request: AIMessageTranslationRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    ai_profile_id = request.ai_config_id
    if not ai_profile_id:
        profiles = m._ai_store().list_profiles()
        ai_profile_id = next((profile.id for profile in profiles if profile.active), profiles[0].id if profiles else "default")
    ai_signature = "|".join((ai_profile_id, connector.settings.provider, connector.settings.model, "v1"))
    cache = m._translation_cache_store()
    target_language = request.target_language
    ordered_messages = []
    missing_messages = []
    translations_by_id = {}
    for item in request.messages:
        message_id = str(item.get("id") or "").strip()
        source_text = str(item.get("text") or "").strip()
        source_language = "en" if str(item.get("sourceLanguage") or "de").casefold() == "en" else "de"
        if not message_id or not source_text:
            raise HTTPException(status_code=422, detail="Für die Übersetzung fehlen ID oder Fehlermeldung.")
        row = {
            "id": message_id,
            "text": source_text,
            "sourceLanguage": source_language,
        }
        ordered_messages.append(row)
        cached = cache.get(ai_signature, source_language, target_language, source_text)
        if cached is None:
            missing_messages.append(row)
        else:
            translations_by_id[message_id] = cached
    try:
        if missing_messages:
            result = connector.translate_messages(
                {
                    "targetLanguage": target_language,
                    "messages": [{"id": item["id"], "text": item["text"]} for item in missing_messages],
                }
            )
            translated = {str(item["id"]): str(item["text"]) for item in result.get("translations") or []}
            for item in missing_messages:
                translated_text = translated[item["id"]]
                translations_by_id[item["id"]] = translated_text
                cache.put(
                    ai_signature,
                    item["sourceLanguage"],
                    target_language,
                    item["text"],
                    translated_text,
                )
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    cache_hits = len(ordered_messages) - len(missing_messages)
    m.log.info(
        "KI-Übersetzung: ai=%s target=%s messages=%s cache_hits=%s cache_misses=%s",
        ai_profile_id,
        target_language,
        len(ordered_messages),
        cache_hits,
        len(missing_messages),
    )
    return {
        "configId": nemo_profile.id,
        "targetLanguage": target_language,
        "translations": [
            {"id": item["id"], "text": translations_by_id[item["id"]]}
            for item in ordered_messages
        ],
        "cache": {"hits": cache_hits, "misses": len(missing_messages)},
    }


@router.post("/api/ai/fields/suggest-rules")
def suggest_ai_rules_for_field(request: AIFieldRuleSuggestionRequest) -> dict:
    from backend import main as m

    nemo_profile, connector = m._resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        with m._nemo_for_config(nemo_profile.id) as (_profile, nemo):
            columns = m.get_columns(nemo=nemo, project=request.project, filter_value="*")
            column = next(
                (
                    item for item in columns
                    if str(item.get("internalName") or "").casefold() == request.internal_name.casefold()
                ),
                None,
            )
            if not column:
                raise HTTPException(status_code=404, detail="Das ausgewählte Feld wurde im NEMO-Projekt nicht gefunden.")
            values = m.load_project_field_values(
                nemo=nemo,
                project=request.project,
                source_column_name=str(column.get("internalName") or request.internal_name),
                max_rows=request.max_rows,
            )
        profile = m.build_anonymized_field_profile(values)
        analysis = connector.suggest_rules_from_profile(
            {
                "internalName": column.get("internalName") or request.internal_name,
                "displayName": column.get("displayName") or request.display_name,
                "description": column.get("description") or request.description,
                "dataType": column.get("dataType") or request.data_type,
                "profile": profile,
                "language": request.language,
            }
        )
    except HTTPException:
        raise
    except m.AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        m.log.exception(
            "Feldprofil oder KI-Regelvorschläge fehlgeschlagen: config=%s project=%s field=%s",
            nemo_profile.id,
            request.project,
            request.internal_name,
        )
        raise HTTPException(status_code=502, detail=f"Das Feld konnte nicht sicher analysiert werden: {exc}") from exc

    m.log.info(
        "Anonymisiertes Feldprofil analysiert: config=%s project=%s field=%s rows=%s suggestions=%s",
        nemo_profile.id,
        request.project,
        request.internal_name,
        profile["sampleSize"],
        len(analysis.get("suggestions") or []),
    )
    return {
        "configId": nemo_profile.id,
        "project": request.project,
        "field": column,
        "profile": profile,
        "analysis": analysis,
    }
