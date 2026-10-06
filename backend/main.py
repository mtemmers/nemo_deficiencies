import json
import hashlib
import os
import re
import logging
import time
import unicodedata
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from backend import __version__
from backend.services.ai_config_store import AIConfigNotFoundError, AIConfigStore, AIConfigStoreError
from backend.services.ai_connector import AIConnectionSettings, AIConnectorError, create_ai_connector
from backend.services.ai_translation_cache_store import AITranslationCacheStore
from backend.services.field_profiler import build_anonymized_field_profile
from backend.services.harmonization import HarmonizationError, build_harmonization_matrix, prepare_group_transfer
from backend.services.config_statistics import build_config_statistics
from backend.services.rules_export import build_rules_csv, RuleStatusFilter
from backend.services.config_store import (
    DEFAULT_NEMO_ENVIRONMENT,
    DEFAULT_NEMO_URL,
    ConfigNotFoundError,
    ConfigProfile,
    ConfigStore,
    build_nemo_config_content,
    config_profile_name,
    get_config_store,
    read_nemo_config_settings,
    update_nemo_config_content,
)
from backend.services.editor_change_log_store import (
    EditorChangeLogStore,
    EditorChangeNotFoundError,
    EditorUndoError,
)
from backend.services.editor_baseline_store import EditorBaselineStore
from backend.services.editor_draft_store import EditorDraftStore
from backend.services.nemo_client import (
    ReportTenantMismatchError,
    create_nemo_client,
    get_columns,
    get_reports,
    load_project_field_values,
    update_reports_sql,
)
from backend.logging_config import configure_logging
from backend.services.report_service import (
    find_report_by_reference,
    run_report_preview,
    summarize_report,
)
from backend.services.report_export import (
    ReportExportError,
    default_export_directory,
    export_reports,
    resolve_export_directory,
    tenant_export_directory,
)
from backend.services.report_utils import (
    filter_deficiency_reports,
    filter_primary_deficiency_reports,
    is_top_25_report,
)
from backend.services.rule_catalog import (
    RuleTemplateResolutionError,
    RuleTemplateValidationError,
    resolve_rule_template,
)
from backend.services.rule_catalog_analysis import analyze_rule_catalog_candidates
from backend.services.rule_catalog_store import (
    RuleCatalogError,
    RuleCatalogStore,
    RuleTemplateNotFoundError,
)
from backend.services.sql_generator import SqlGenerationError, render_sql_from_model, render_top_25_sql
from backend.services.sql_model import get_rule_catalog, merge_missing_group_metadata, normalize_editor_model, parse_editor_model
from backend.export_connectors import (
    ExportConnectorError,
    get_connector,
    list_connectors,
)
import backend.export_connectors  # noqa: F401 – trigger auto-discovery at import time

PACKAGE_ROOT = Path(__file__).resolve().parent


def _application_home() -> Path:
    configured_home = os.getenv("NEMO_DEFICIENCIES_HOME")
    if configured_home:
        return Path(configured_home).expanduser().resolve()
    local_app_data = os.getenv("LOCALAPPDATA")
    return (Path(local_app_data) / "NEMO Deficiencies") if local_app_data else (Path.home() / ".nemo_deficiencies")


PROJECT_ROOT = _application_home()
FRONTEND_DIR = PACKAGE_ROOT / "frontend"
DEFAULT_PROJECT = "Master Data"
STANDARD_PROJECTS = ("Master Data", "Business Processes")
LOG_FILE = configure_logging(PROJECT_ROOT)
log = logging.getLogger(__name__)
request_id_context: ContextVar[str] = ContextVar("request_id", default="")

app = FastAPI(title="NEMO Deficiencies API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.middleware("http")
async def log_api_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    request_id_context.set(request_id)
    started = time.perf_counter()
    log.info("[%s] API start: %s %s", request_id, request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - started) * 1000
        log.exception(
            "[%s] API exception: %s %s duration_ms=%.1f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise
    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    log.log(
        logging.WARNING if response.status_code >= 400 else logging.INFO,
        "[%s] API end: %s %s status=%s duration_ms=%.1f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def log_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", uuid.uuid4().hex[:12])
    log.warning(
        "[%s] HTTP error: %s %s status=%s detail=%s",
        request_id,
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    headers = dict(exc.headers or {})
    headers["X-Request-ID"] = request_id
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)


class ConfigWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=120)
    ini_content: str = Field(alias="iniContent", min_length=1)
    source_file: Optional[str] = Field(default="", alias="sourceFile")


class ConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    ini_content: Optional[str] = Field(default=None, alias="iniContent", min_length=1)
    source_file: Optional[str] = Field(default=None, alias="sourceFile")


class ConfigCredentialsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    tenant: str = Field(min_length=1, max_length=120, pattern=r"^[^\r\n]+$")
    userid: str = Field(min_length=1, max_length=240, pattern=r"^[^\r\n]+$")
    password: str = Field(min_length=1, max_length=1024, pattern=r"^[^\r\n]+$")
    nemo_url: str = Field(
        default=DEFAULT_NEMO_URL,
        alias="nemoUrl",
        min_length=1,
        max_length=500,
        pattern=r"^https?://[^\s]+$",
    )
    environment: str = Field(
        default=DEFAULT_NEMO_ENVIRONMENT,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9._-]+$",
    )


class ConfigConnectionUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=120)
    tenant: str = Field(min_length=1, max_length=120, pattern=r"^[^\r\n]+$")
    userid: str = Field(min_length=1, max_length=240, pattern=r"^[^\r\n]+$")
    password: str = Field(default="", max_length=1024, pattern=r"^[^\r\n]*$")
    nemo_url: str = Field(
        alias="nemoUrl",
        min_length=1,
        max_length=500,
        pattern=r"^https?://[^\s]+$",
    )
    environment: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9._-]+$")


class AIConfigCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(default="Groq", min_length=1, max_length=120)
    provider: str = Field(
        default="groq",
        pattern=r"^(groq|openai|perplexity|gemini|ollama|lmstudio|openai_compatible)$",
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
    project: str = Field(default=DEFAULT_PROJECT, min_length=1, max_length=120)
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



class EditorModelRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    editor_model: dict = Field(alias="editorModel")


class NemoReportWriteRequest(EditorModelRequest):
    overwrite_confirmation: str = Field(alias="overwriteConfirmation", min_length=1, max_length=240)

class EditorDraftRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    editor_model: dict = Field(alias="editorModel")
    base_sql_hash: str = Field(default="", alias="baseSqlHash", pattern=r"^[0-9a-f]{0,64}$")


class EditorChangePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    change_type: str = Field(alias="changeType", min_length=1, max_length=80)
    target_path: str = Field(alias="targetPath", min_length=1, max_length=240)
    target_label: str = Field(default="", alias="targetLabel", max_length=240)
    old_value: Any = Field(default=None, alias="oldValue")
    new_value: Any = Field(default=None, alias="newValue")
    note: str = Field(default="", max_length=500)


class EditorChangeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    editor_model: dict = Field(alias="editorModel")
    base_sql_hash: str = Field(default="", alias="baseSqlHash", pattern=r"^[0-9a-f]{0,64}$")
    change: EditorChangePayload


class EditorUndoRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    base_sql_hash: str = Field(default="", alias="baseSqlHash", pattern=r"^[0-9a-f]{0,64}$")


class HarmonizationTransferRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    field_key: str = Field(alias="fieldKey", min_length=1, max_length=240)
    source_report_id: str = Field(alias="sourceReportId", min_length=1, max_length=240)
    target_report_ids: list[str] = Field(alias="targetReportIds", min_length=1, max_length=100)


class RuleTemplateCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=240)
    description: str = Field(default="", max_length=2000)
    status: str = Field(default="draft", pattern=r"^(draft|approved|deprecated)$")
    condition_template: str = Field(alias="conditionTemplate", min_length=1, max_length=100_000)
    message_de_template: str = Field(default="", alias="messageDeTemplate", max_length=2000)
    message_en_template: str = Field(default="", alias="messageEnTemplate", max_length=2000)
    dimension: str = Field(min_length=1, max_length=120)
    rule_type: str = Field(alias="ruleType", min_length=1, max_length=120)
    parameter_schema: dict = Field(default_factory=dict, alias="parameterSchema")
    compatible_data_types: list[str] = Field(default_factory=list, alias="compatibleDataTypes", max_length=100)
    field_categories: list[str] = Field(default_factory=list, alias="fieldCategories", max_length=100)
    examples: list[dict] = Field(default_factory=list, max_length=100)
    change_note: str = Field(default="Initiale Version", alias="changeNote", max_length=1000)


class RuleTemplateVersionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    condition_template: str = Field(alias="conditionTemplate", min_length=1, max_length=100_000)
    message_de_template: str = Field(default="", alias="messageDeTemplate", max_length=2000)
    message_en_template: str = Field(default="", alias="messageEnTemplate", max_length=2000)
    dimension: str = Field(min_length=1, max_length=120)
    rule_type: str = Field(alias="ruleType", min_length=1, max_length=120)
    parameter_schema: dict = Field(default_factory=dict, alias="parameterSchema")
    compatible_data_types: list[str] = Field(default_factory=list, alias="compatibleDataTypes", max_length=100)
    field_categories: list[str] = Field(default_factory=list, alias="fieldCategories", max_length=100)
    examples: list[dict] = Field(default_factory=list, max_length=100)
    change_note: str = Field(default="", alias="changeNote", max_length=1000)


class RuleTemplateMetadataRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=240)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, pattern=r"^(draft|approved|deprecated)$")


class RuleTemplateResolveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: Optional[int] = Field(default=None, ge=1)
    field: str = Field(min_length=1, max_length=240)
    display_name: str = Field(default="", alias="displayName", max_length=500)
    description: str = Field(default="", max_length=2000)
    parameters: dict = Field(default_factory=dict)


class RuleTemplateBindingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    template_id: str = Field(alias="templateId", min_length=1, max_length=240)
    template_version: int = Field(alias="templateVersion", ge=1)
    config_id: str = Field(alias="configId", min_length=1, max_length=240)
    project: str = Field(min_length=1, max_length=240)
    report_ref: str = Field(alias="reportRef", min_length=1, max_length=500)
    group_ref: str = Field(alias="groupRef", min_length=1, max_length=500)
    rule_ref: str = Field(alias="ruleRef", min_length=1, max_length=500)
    parameters: dict = Field(default_factory=dict)


class EditorExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    editor_model: dict = Field(alias="editorModel")
    format: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9_]+$")
    options: dict = Field(default_factory=dict)


class RuleCatalogAnalysisRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = Field(default=DEFAULT_PROJECT, pattern=r"^Master Data$")


class RuleCatalogImportRequest(RuleCatalogAnalysisRequest):
    candidate_keys: list[str] = Field(alias="candidateKeys", min_length=1, max_length=5000)


class RuleCatalogCandidateDecisionRequest(RuleCatalogAnalysisRequest):
    candidate_key: str = Field(alias="candidateKey", min_length=1, max_length=240)
    decision: str = Field(pattern=r"^(rejected|pending)$")


class ReportRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = DEFAULT_PROJECT
    max_rows: int = Field(default=100, alias="maxRows", ge=1, le=1000)


class ReportExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: str = Field(alias="configId", min_length=1, max_length=120)
    project: str = Field(default=DEFAULT_PROJECT, min_length=1, max_length=240)
    action: str = Field(pattern=r"^(sql|data)$")
    selection_mode: str = Field(alias="selectionMode", pattern=r"^(all|exact|contains)$")
    report_refs: list[str] = Field(default_factory=list, alias="reportRefs", max_length=5000)
    contains_values: list[str] = Field(default_factory=list, alias="containsValues", max_length=5000)
    output_dir: str = Field(default="", alias="outputDir", max_length=1000)
    refresh_index: bool = Field(default=False, alias="refreshIndex")


def _store() -> ConfigStore:
    return get_config_store(PROJECT_ROOT)

def _draft_store() -> EditorDraftStore:
    return EditorDraftStore(_store().db_path)


def _baseline_store() -> EditorBaselineStore:
    return EditorBaselineStore(_store().db_path)


def _change_store() -> EditorChangeLogStore:
    return EditorChangeLogStore(_store().db_path)


def _translation_cache_store() -> AITranslationCacheStore:
    return AITranslationCacheStore(_store().db_path)


def _rule_template_store() -> RuleCatalogStore:
    store = RuleCatalogStore(_store().db_path)
    store.ensure_default_templates()
    return store


def _editor_storage_ref(config_id: str, project: str, report_ref: str) -> str:
    baseline_store = _baseline_store()
    if baseline_store.get_baseline(config_id, project, report_ref):
        return report_ref
    return baseline_store.find_report_ref_by_internal_name(config_id, project, report_ref) or report_ref


def _editor_model_report_references(editor_model: dict) -> set[str]:
    report = editor_model.get("report") or {}
    return {
        str(value).strip().casefold()
        for value in (report.get("id"), report.get("internalName"), report.get("displayName"))
        if str(value or "").strip()
    }


def _editor_model_matches_report(editor_model: dict, report: dict) -> bool:
    model_references = _editor_model_report_references(editor_model)
    report_references = {
        str(value).strip().casefold()
        for value in (report.get("id"), report.get("internalName"), report.get("displayName"))
        if str(value or "").strip()
    }
    return not model_references or not report_references or bool(model_references & report_references)


def _sql_fingerprint(sql: str) -> str:
    normalized = "\n".join(
        line.rstrip()
        for line in str(sql or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _discard_stale_editor_draft(
    *,
    config_id: str,
    project: str,
    report_ref: str,
    current_sql: str,
    current_model: dict,
    baseline,
    draft,
    draft_store: EditorDraftStore,
) -> tuple[Any, bool]:
    if draft is None:
        return None, False
    current_hash = _sql_fingerprint(current_sql)
    draft_base_hash = draft.baseSqlHash or _sql_fingerprint(baseline.originalSql)
    if draft_base_hash == current_hash:
        return draft, False

    log.warning(
        "Veralteter Editor-Draft archiviert: config=%s project=%s report=%s draft=%s base=%s current=%s",
        config_id,
        project,
        report_ref,
        draft.id,
        draft_base_hash[:12],
        current_hash[:12],
    )
    change_store = _change_store()
    change_store.invalidate_undoable_changes(config_id, project, report_ref)
    audit_change = change_store.append_change(
        config_id=config_id,
        project=project,
        report_ref=report_ref,
        change_type="external_report_refresh",
        target_path="$",
        target_label="NEMO-Bericht extern aktualisiert",
        old_value=normalize_editor_model(draft.editorModel),
        new_value=normalize_editor_model(current_model),
        note="Alter Draft archiviert; aktuelles SQL erneut aus NEMO geladen.",
    )
    change_store.mark_undone(audit_change.id)
    draft_store.delete_draft(config_id, project, report_ref)
    return None, True


def _ensure_editor_model_matches_report(editor_model: dict, report: dict) -> None:
    if _editor_model_matches_report(editor_model, report):
        return
    expected = str(report.get("displayName") or report.get("internalName") or "den ausgewählten Bericht")
    raise HTTPException(
        status_code=409,
        detail=f"Das Editor-Modell gehört zu einem anderen Bericht. Bitte '{expected}' neu laden.",
    )


def _ai_store() -> AIConfigStore:
    return AIConfigStore(PROJECT_ROOT)


def _resolve_ai_connector(config_id: Optional[str], ai_config_id: Optional[str] = None):
    try:
        nemo_profile = _store().resolve_profile(config_id)
        settings = _ai_store().resolve_settings(ai_config_id)
    except (ConfigNotFoundError, AIConfigNotFoundError) as exc:
        raise _http_not_found(exc) from exc
    except AIConfigStoreError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return nemo_profile, create_ai_connector(settings)


def _http_not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@contextmanager
def _nemo_for_config(config_id: Optional[str]) -> Iterator[tuple[ConfigProfile, object]]:
    store = _store()
    try:
        profile = store.resolve_profile(config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc

    with store.temporary_config_file(profile.id) as config_path:
        yield profile, create_nemo_client(config_path)


def _load_reports(config_id: Optional[str], project: str, deficiencies_only: bool) -> tuple[ConfigProfile, list[dict]]:
    try:
        with _nemo_for_config(config_id) as (profile, nemo):
            reports = get_reports(nemo=nemo, project=project, filter_value="*")
    except HTTPException:
        raise
    except Exception as exc:
        detail = _nemo_error_summary(exc)
        normalized = str(exc).casefold()
        if "incorrect username or password" in normalized or "notauthorizedexception" in normalized:
            raise HTTPException(
                status_code=401,
                detail=(
                    "NEMO-Anmeldung fehlgeschlagen. Bitte die ausgewählte Konfiguration bearbeiten "
                    "und User-ID, Passwort, NEMO-URL sowie Environment prüfen."
                ),
            ) from exc
        raise HTTPException(status_code=502, detail=f"Berichte konnten nicht aus NEMO geladen werden: {detail}") from exc
    if deficiencies_only:
        reports = filter_primary_deficiency_reports(reports)
    return profile, reports


@app.get("/", include_in_schema=False)
def app_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/cli-wizard", include_in_schema=False)
def cli_wizard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "cli-wizard.html")


@app.get("/api/cli-wizard/defaults")
def cli_wizard_defaults() -> dict:
    return {"outputDir": str(default_export_directory())}


@app.post("/api/cli-wizard/export")
def run_cli_wizard_export(request: ReportExportRequest) -> dict:
    if request.selection_mode == "exact" and not request.report_refs:
        raise HTTPException(status_code=422, detail="Bitte mindestens einen Bericht auswählen.")
    if request.selection_mode == "contains" and not request.contains_values:
        raise HTTPException(status_code=422, detail="Bitte mindestens einen Suchbegriff eingeben.")

    report_refs = request.report_refs if request.selection_mode == "exact" else []
    contains_values = request.contains_values if request.selection_mode == "contains" else []
    base_output_dir = resolve_export_directory(request.output_dir)
    try:
        with _nemo_for_config(request.config_id) as (profile, nemo):
            output_dir = tenant_export_directory(base_output_dir, profile.tenant or profile.name)
            all_reports = get_reports(nemo=nemo, project=request.project, filter_value="*")
            result = export_reports(
                nemo=nemo,
                project=request.project,
                all_reports=all_reports,
                report_refs=report_refs,
                contains_values=contains_values,
                output_dir=output_dir,
                export_data=request.action == "data",
                refresh_index=request.refresh_index,
            )
    except (OSError, ReportExportError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log.info(
        "CLI-Wizard-Export abgeschlossen: config=%s project=%s reports=%s output=%s",
        profile.id,
        request.project,
        result["selectedReportCount"],
        result["outputDir"],
    )
    return {"configId": profile.id, "tenant": profile.tenant, "project": request.project, **result}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/api/configs")
def list_configs() -> dict:
    profiles = _store().list_profiles()
    return {
        "configs": [profile.to_dict() for profile in profiles],
        "defaultConfigId": _store().default_profile(profiles).id if profiles else None,
    }


@app.post("/api/configs", status_code=201)
def create_config(request: ConfigWriteRequest) -> dict:
    profile = _store().create_config(
        name=request.name,
        ini_content=request.ini_content,
        source_file=request.source_file or "",
    )
    return {"config": profile.to_dict()}


@app.post("/api/configs/from-credentials", status_code=201)
def create_config_from_credentials(request: ConfigCredentialsRequest) -> dict:
    try:
        name = request.name.strip() if request.name else config_profile_name(request.tenant)
        ini_content = build_nemo_config_content(
            request.tenant,
            request.userid,
            request.password,
            nemo_url=request.nemo_url,
            environment=request.environment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    store = _store()
    if any(profile.name.casefold() == name.casefold() for profile in store.list_profiles()):
        raise HTTPException(status_code=409, detail=f"Die Konfiguration '{name}' ist bereits vorhanden.")
    profile = store.create_config(name=name, ini_content=ini_content)
    log.info("Config-Profil über Oberfläche angelegt: id=%s name=%s tenant=%s", profile.id, profile.name, profile.tenant)
    return {"config": profile.to_dict()}


@app.get("/api/configs/{config_id}/connection")
def get_config_connection(config_id: str) -> dict:
    try:
        store = _store()
        profile = store.get_profile(config_id)
        settings = read_nemo_config_settings(store.decrypt_config(config_id))
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"config": {"id": profile.id, "name": profile.name, **settings}}


@app.put("/api/configs/{config_id}/connection")
def update_config_connection(config_id: str, request: ConfigConnectionUpdateRequest) -> dict:
    store = _store()
    try:
        profile = store.get_profile(config_id)
        duplicate = next(
            (
                item
                for item in store.list_profiles()
                if item.id != config_id and item.name.casefold() == request.name.strip().casefold()
            ),
            None,
        )
        if duplicate:
            raise HTTPException(status_code=409, detail=f"Die Konfiguration '{request.name.strip()}' ist bereits vorhanden.")
        ini_content = update_nemo_config_content(
            store.decrypt_config(config_id),
            tenant=request.tenant,
            userid=request.userid,
            password=request.password,
            nemo_url=request.nemo_url,
            environment=request.environment,
        )
        updated = store.update_config(config_id, name=request.name, ini_content=ini_content)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    log.info(
        "Config-Profil über Oberfläche geändert: id=%s name=%s tenant=%s environment=%s",
        updated.id,
        updated.name,
        updated.tenant,
        request.environment,
    )
    return {"config": updated.to_dict(), "passwordChanged": bool(request.password), "previousName": profile.name}


@app.put("/api/configs/{config_id}")
def update_config(config_id: str, request: ConfigUpdateRequest) -> dict:
    try:
        profile = _store().update_config(
            config_id=config_id,
            name=request.name,
            ini_content=request.ini_content,
            source_file=request.source_file,
        )
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    return {"config": profile.to_dict()}


@app.delete("/api/configs/{config_id}", status_code=204)
def delete_config(config_id: str) -> None:
    try:
        _store().delete_config(config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc


@app.post("/api/configs/import-local")
def import_local_configs(overwrite: bool = Query(default=False)) -> dict:
    profiles = _store().import_ini_files(overwrite=overwrite)
    return {
        "count": len(profiles),
        "configs": [profile.to_dict() for profile in profiles],
    }


@app.get("/api/ai/configs")
def list_ai_configs() -> dict:
    profiles = _ai_store().list_profiles()
    return {
        "configs": [profile.to_dict() for profile in profiles],
        "defaultAiConfigId": profiles[0].id if profiles else None,
    }


@app.post("/api/ai/configs", status_code=201)
def create_ai_config(request: AIConfigCreateRequest) -> dict:
    try:
        connector = create_ai_connector(
            AIConnectionSettings(
                provider=request.provider,
                base_url=request.base_url,
                model=request.model,
                api_key=request.api_key,
            )
        )
        connector.test_connection()
        profile = _ai_store().create_profile(
            name=request.name,
            provider=request.provider,
            base_url=request.base_url,
            model=request.model,
            api_key=request.api_key,
        )
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIConfigStoreError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    log.info("KI-Konfiguration angelegt: id=%s provider=%s model=%s", profile.id, profile.provider, profile.model)
    return {"config": profile.to_dict()}


@app.post("/api/ai/configs/{ai_config_id}/test")
def test_ai_config(ai_config_id: str) -> dict:
    try:
        connector = create_ai_connector(_ai_store().resolve_settings(ai_config_id))
        return connector.test_connection()
    except AIConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except AIConfigStoreError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/ai/rules/draft")
def create_ai_rule_draft(request: AIRuleDraftRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        draft = connector.create_rule_draft(request.model_dump(by_alias=True))
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "draft": draft}


@app.post("/api/ai/rules/test-examples")
def test_ai_rule_examples(request: AIRuleExampleTestRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        result = connector.test_rule_examples(request.model_dump(by_alias=True))
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "test": result, "testType": "semantic-ai-review"}


@app.post("/api/ai/rules/explain")
def explain_ai_rule(request: AIRuleExplanationRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        explanation = connector.explain_rule(request.model_dump(by_alias=True))
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "explanation": explanation}


@app.post("/api/ai/rules/revise")
def revise_ai_rule(request: AIRuleRevisionRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        revision = connector.revise_rule(request.model_dump(by_alias=True))
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"configId": nemo_profile.id, "revision": revision}


@app.post("/api/ai/messages/translate")
def translate_ai_messages(request: AIMessageTranslationRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    ai_profile_id = request.ai_config_id
    if not ai_profile_id:
        profiles = _ai_store().list_profiles()
        ai_profile_id = next((profile.id for profile in profiles if profile.active), profiles[0].id if profiles else "default")
    ai_signature = "|".join((ai_profile_id, connector.settings.provider, connector.settings.model, "v1"))
    cache = _translation_cache_store()
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
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    cache_hits = len(ordered_messages) - len(missing_messages)
    log.info(
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


@app.post("/api/ai/fields/suggest-rules")
def suggest_ai_rules_for_field(request: AIFieldRuleSuggestionRequest) -> dict:
    nemo_profile, connector = _resolve_ai_connector(request.config_id, request.ai_config_id)
    try:
        with _nemo_for_config(nemo_profile.id) as (_profile, nemo):
            columns = get_columns(nemo=nemo, project=request.project, filter_value="*")
            column = next(
                (
                    item for item in columns
                    if str(item.get("internalName") or "").casefold() == request.internal_name.casefold()
                ),
                None,
            )
            if not column:
                raise HTTPException(status_code=404, detail="Das ausgewählte Feld wurde im NEMO-Projekt nicht gefunden.")
            values = load_project_field_values(
                nemo=nemo,
                project=request.project,
                source_column_name=str(column.get("internalName") or request.internal_name),
                max_rows=request.max_rows,
            )
        profile = build_anonymized_field_profile(values)
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
    except AIConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        log.exception(
            "Feldprofil oder KI-Regelvorschläge fehlgeschlagen: config=%s project=%s field=%s",
            nemo_profile.id,
            request.project,
            request.internal_name,
        )
        raise HTTPException(status_code=502, detail=f"Das Feld konnte nicht sicher analysiert werden: {exc}") from exc

    log.info(
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



@app.get("/api/rule-catalog")
def rule_catalog() -> dict:
    return get_rule_catalog()


@app.get("/api/rule-templates")
def list_rule_templates(
    status: Optional[str] = Query(default=None, pattern=r"^(draft|approved|deprecated)$"),
) -> dict:
    templates = _rule_template_store().list_templates(status=status)
    return {"count": len(templates), "templates": [template.to_dict() for template in templates]}


@app.post("/api/rule-templates/analyze-existing")
def analyze_existing_rule_templates(request: RuleCatalogAnalysisRequest) -> dict:
    profile, report_models, _columns, skipped_reports = _load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = _rule_template_store()
    analysis = analyze_rule_catalog_candidates(
        report_models,
        store.list_templates(),
    )
    decisions = store.list_candidate_decisions(config_id=profile.id, project=request.project)
    for candidate in analysis["candidates"]:
        candidate["decision"] = decisions.get(candidate["key"], "pending")
    return {
        "configId": profile.id,
        "project": request.project,
        **analysis,
        "skippedReports": skipped_reports,
    }


@app.post("/api/rule-templates/import-existing")
def import_existing_rule_templates(request: RuleCatalogImportRequest) -> dict:
    profile, report_models, _columns, skipped_reports = _load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = _rule_template_store()
    analysis = analyze_rule_catalog_candidates(report_models, store.list_templates())
    by_key = {candidate["key"]: candidate for candidate in analysis["candidates"]}
    selected = []
    for key in dict.fromkeys(request.candidate_keys):
        candidate = by_key.get(key)
        if not candidate:
            raise HTTPException(status_code=422, detail=f"Analysekandidat nicht gefunden: {key}")
        selected.append(candidate)

    imported = []
    binding_count = 0
    for candidate in selected:
        try:
            if candidate["existingTemplateId"]:
                template = store.get_template(candidate["existingTemplateId"])
                created = False
            else:
                template = store.create_template(
                    key=candidate["key"],
                    name=candidate["name"],
                    description=candidate["description"],
                    status="draft",
                    condition_template=candidate["conditionTemplate"],
                    message_de_template=candidate["messageDeTemplate"],
                    message_en_template=candidate["messageEnTemplate"],
                    dimension=candidate["dimension"],
                    rule_type=candidate["ruleType"],
                    parameter_schema=candidate["parameterSchema"],
                    compatible_data_types=candidate["compatibleDataTypes"],
                    field_categories=candidate["fieldCategories"],
                    change_note="Automatisch aus bestehenden Master-Data-Regeln analysiert",
                )
                created = True
            for location in candidate["locations"]:
                store.bind_rule(
                    template_ref=template.id,
                    template_version=template.currentVersion,
                    config_id=profile.id,
                    project=request.project,
                    report_ref=location["reportRef"],
                    group_ref=location["groupRef"],
                    rule_ref=location["ruleRef"],
                    parameters=location.get("parameters") or {},
                )
                binding_count += 1
        except (RuleCatalogError, RuleTemplateValidationError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        imported.append(
            {
                "candidateKey": candidate["key"],
                "template": template.to_dict(),
                "created": created,
                "bindingCount": len(candidate["locations"]),
            }
        )
        store.set_candidate_decision(
            config_id=profile.id,
            project=request.project,
            candidate_key=candidate["key"],
            decision="imported",
        )
    return {
        "configId": profile.id,
        "project": request.project,
        "importedCount": len(imported),
        "createdCount": sum(1 for item in imported if item["created"]),
        "bindingCount": binding_count,
        "imported": imported,
        "skippedReports": skipped_reports,
    }


@app.post("/api/rule-templates/candidate-decisions")
def set_rule_template_candidate_decision(request: RuleCatalogCandidateDecisionRequest) -> dict:
    profile, report_models, _columns, _skipped_reports = _load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = _rule_template_store()
    analysis = analyze_rule_catalog_candidates(report_models, store.list_templates())
    candidate = next(
        (item for item in analysis["candidates"] if item["key"] == request.candidate_key),
        None,
    )
    if not candidate:
        raise HTTPException(status_code=422, detail=f"Analysekandidat nicht gefunden: {request.candidate_key}")
    stored_decision = None if request.decision == "pending" else request.decision
    store.set_candidate_decision(
        config_id=profile.id,
        project=request.project,
        candidate_key=request.candidate_key,
        decision=stored_decision,
    )
    return {
        "configId": profile.id,
        "project": request.project,
        "candidateKey": request.candidate_key,
        "decision": request.decision,
    }


@app.get("/api/rule-templates/{template_ref}")
def get_rule_template(
    template_ref: str,
    version: Optional[int] = Query(default=None, ge=1),
) -> dict:
    try:
        template = _rule_template_store().get_template(template_ref, version=version)
    except RuleTemplateNotFoundError as exc:
        raise _http_not_found(exc) from exc
    return {"template": template.to_dict()}


@app.post("/api/rule-templates", status_code=201)
def create_rule_template(request: RuleTemplateCreateRequest) -> dict:
    try:
        template = _rule_template_store().create_template(
            key=request.key,
            name=request.name,
            description=request.description,
            status=request.status,
            condition_template=request.condition_template,
            message_de_template=request.message_de_template,
            message_en_template=request.message_en_template,
            dimension=request.dimension,
            rule_type=request.rule_type,
            parameter_schema=request.parameter_schema,
            compatible_data_types=request.compatible_data_types,
            field_categories=request.field_categories,
            examples=request.examples,
            change_note=request.change_note,
        )
    except (RuleCatalogError, RuleTemplateValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@app.post("/api/rule-templates/{template_ref}/versions", status_code=201)
def create_rule_template_version(template_ref: str, request: RuleTemplateVersionRequest) -> dict:
    try:
        template = _rule_template_store().add_version(
            template_ref,
            condition_template=request.condition_template,
            message_de_template=request.message_de_template,
            message_en_template=request.message_en_template,
            dimension=request.dimension,
            rule_type=request.rule_type,
            parameter_schema=request.parameter_schema,
            compatible_data_types=request.compatible_data_types,
            field_categories=request.field_categories,
            examples=request.examples,
            change_note=request.change_note,
        )
    except RuleTemplateNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except (RuleCatalogError, RuleTemplateValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@app.patch("/api/rule-templates/{template_ref}")
def update_rule_template_metadata(template_ref: str, request: RuleTemplateMetadataRequest) -> dict:
    try:
        template = _rule_template_store().update_metadata(
            template_ref,
            name=request.name,
            description=request.description,
            status=request.status,
        )
    except RuleTemplateNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except RuleCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@app.post("/api/rule-templates/{template_ref}/resolve")
def resolve_catalog_rule(template_ref: str, request: RuleTemplateResolveRequest) -> dict:
    try:
        template = _rule_template_store().get_template(template_ref, version=request.version)
        resolved = resolve_rule_template(
            template.version,
            field=request.field,
            display_name=request.display_name,
            description=request.description,
            parameters=request.parameters,
        )
    except RuleTemplateNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except (RuleTemplateValidationError, RuleTemplateResolutionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict(), "resolvedRule": resolved.to_dict()}


@app.post("/api/rule-template-bindings", status_code=201)
def bind_catalog_rule(request: RuleTemplateBindingRequest) -> dict:
    try:
        binding = _rule_template_store().bind_rule(
            template_ref=request.template_id,
            template_version=request.template_version,
            config_id=request.config_id,
            project=request.project,
            report_ref=request.report_ref,
            group_ref=request.group_ref,
            rule_ref=request.rule_ref,
            parameters=request.parameters,
        )
    except RuleTemplateNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except RuleCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"binding": binding.to_dict()}


@app.post("/api/editor-model/validate")
def validate_editor_model_request(request: EditorModelRequest) -> dict:
    model = normalize_editor_model(request.editor_model)
    return {
        "summary": model["summary"],
        "validation": model["validation"],
        "editorModel": model,
    }

@app.get("/api/projects")
def list_projects() -> dict:
    return {
        "projects": [
            {"id": project, "name": project, "default": project == DEFAULT_PROJECT}
            for project in STANDARD_PROJECTS
        ],
        "defaultProject": DEFAULT_PROJECT,
    }


@app.get("/api/projects/{project}/columns")
def list_project_columns(
    project: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
) -> dict:
    with _nemo_for_config(config_id) as (profile, nemo):
        columns = get_columns(nemo=nemo, project=project, filter_value="*")
    return {
        "configId": profile.id,
        "configTenant": profile.tenant,
        "project": project,
        "count": len(columns),
        "columns": columns,
    }


@app.get("/api/reports")
def list_reports(
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
    deficiencies_only: bool = Query(default=True, alias="deficienciesOnly"),
) -> dict:
    profile, reports = _load_reports(config_id, project, deficiencies_only)
    return {
        "configId": profile.id,
        "configTenant": profile.tenant,
        "project": project,
        "deficienciesOnly": deficiencies_only,
        "count": len(reports),
        "reports": [summarize_report(report) for report in reports],
    }


@app.get("/api/harmonization")
def get_harmonization_matrix(
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
) -> dict:
    profile, report_models, columns, skipped_reports = _load_harmonization_context(config_id, project)
    matrix = build_harmonization_matrix(report_models, columns)
    return {
        "configId": profile.id,
        "project": project,
        **matrix,
        "skippedReports": skipped_reports,
    }


@app.get("/api/config-statistics")
def get_config_statistics(
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
) -> dict:
    profile, report_models, _columns, skipped_reports = _load_harmonization_context(config_id, project)
    statistics = build_config_statistics(report_models, skipped_reports)
    return {
        "configId": profile.id,
        "configName": profile.name,
        "configTenant": profile.tenant,
        "project": project,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **statistics,
    }


@app.get("/api/statistics/export-rules")
def export_statistics_rules(
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
    report_id: Optional[str] = Query(default=None, alias="reportId"),
    active_only: str = Query(default="both", alias="activeOnly"),
    language: str = Query(default="de"),
) -> Response:
    """
    Export detailed rule overview as CSV.
    
    Query parameters:
    - configId: Configuration ID
    - project: Project name (default: "Master Data")
    - reportId: Optional report ID to filter (null/empty = all reports)
    - activeOnly: "active", "inactive", or "both" (default)
    - language: "de" or "en" (default: "de")
    """
    profile, report_models, _columns, _skipped_reports = _load_harmonization_context(config_id, project)
    
    # Validate status filter
    status_filter = active_only.lower()
    if status_filter not in ("active", "inactive", "both"):
        status_filter = "both"
    
    # Generate CSV
    csv_content = build_rules_csv(
        report_models=report_models,
        report_id_filter=report_id if report_id and report_id.strip() else None,
        status_filter=status_filter,
        language=language,
    )
    
    # Build filename
    report_suffix = f"_{report_id}" if report_id and report_id.strip() else "_all"
    status_suffix = f"_{active_only.lower()}" if active_only.lower() != "both" else ""
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    filename = f"rules_export{report_suffix}{status_suffix}_{timestamp}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/harmonization/preview")
def preview_harmonization_transfer(request: HarmonizationTransferRequest) -> dict:
    profile, report_models, columns, skipped_reports = _load_harmonization_context(
        request.config_id,
        request.project,
    )
    try:
        plan = prepare_group_transfer(
            report_models,
            columns,
            request.field_key,
            request.source_report_id,
            request.target_report_ids,
        )
    except HarmonizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "configId": profile.id,
        "project": request.project,
        **_public_harmonization_plan(plan),
        "skippedReports": skipped_reports,
    }


@app.post("/api/harmonization/apply")
def apply_harmonization_transfer(request: HarmonizationTransferRequest) -> dict:
    profile, report_models, columns, skipped_reports = _load_harmonization_context(
        request.config_id,
        request.project,
    )
    try:
        plan = prepare_group_transfer(
            report_models,
            columns,
            request.field_key,
            request.source_report_id,
            request.target_report_ids,
        )
    except HarmonizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    applied = []
    draft_store = _draft_store()
    change_store = _change_store()
    source_hashes = {
        str((item.get("report") or {}).get("internalName") or (item.get("report") or {}).get("id") or ""):
        str(item.get("sourceSqlHash") or "")
        for item in report_models
    }
    for change in plan["changes"]:
        report_ref = change["reportId"]
        storage_ref = _editor_storage_ref(profile.id, request.project, report_ref)
        draft = draft_store.save_draft(
            config_id=profile.id,
            project=request.project,
            report_ref=storage_ref,
            editor_model=change["editorModel"],
            base_sql_hash=source_hashes.get(report_ref, ""),
        )
        log_entry = change_store.append_change(
            config_id=profile.id,
            project=request.project,
            report_ref=storage_ref,
            change_type=f"harmonization_group_{change['action']}",
            target_path="$",
            target_label=f"Harmonisierung · {plan['source']['internalName']}",
            old_value=change["oldModel"],
            new_value=change["editorModel"],
            note=f"Übernommen aus {plan['source']['reportName']}",
        )
        applied.append(
            {
                "reportId": report_ref,
                "reportName": change["reportName"],
                "draft": draft.to_dict(),
                "change": log_entry.to_dict(),
            }
        )
    log.info(
        "Harmonisierung angewendet: config=%s project=%s field=%s source=%s targets=%s",
        profile.id,
        request.project,
        request.field_key,
        request.source_report_id,
        [entry["reportId"] for entry in applied],
    )
    return {
        "configId": profile.id,
        "project": request.project,
        **_public_harmonization_plan(plan),
        "applied": applied,
        "skippedReports": skipped_reports,
    }


def _load_harmonization_context(
    config_id: Optional[str],
    project: str,
) -> tuple[ConfigProfile, list[dict], list[dict], list[dict]]:
    with _nemo_for_config(config_id) as (profile, nemo):
        reports = filter_deficiency_reports(get_reports(nemo=nemo, project=project, filter_value="*"))
        columns = get_columns(nemo=nemo, project=project, filter_value="*")
    report_models = []
    skipped_reports = []
    for report in reports:
        report_name = str(report.get("displayName") or report.get("internalName") or "")
        if is_top_25_report(report):
            continue
        report_ref = str(report.get("internalName") or report.get("id") or report_name)
        try:
            original_sql = report.get("querySyntax") or ""
            original_model = parse_editor_model(original_sql, report)
            storage_ref = _editor_storage_ref(profile.id, project, report_ref)
            baseline = _baseline_store().capture_if_missing(
                profile.id,
                project,
                storage_ref,
                original_sql,
                normalize_editor_model(original_model),
            )
            draft_store = _draft_store()
            draft = draft_store.get_draft(profile.id, project, storage_ref)
            if draft and not _editor_model_matches_report(draft.editorModel, report):
                draft_store.delete_draft(profile.id, project, storage_ref)
                draft = None
            if draft:
                draft, _stale_draft_discarded = _discard_stale_editor_draft(
                    config_id=profile.id,
                    project=project,
                    report_ref=storage_ref,
                    current_sql=original_sql,
                    current_model=original_model,
                    baseline=baseline,
                    draft=draft,
                    draft_store=draft_store,
                )
            model = (
                merge_missing_group_metadata(normalize_editor_model(draft.editorModel), original_model)
                if draft
                else original_model
            )
            report_models.append(
                {
                    "report": summarize_report(report),
                    "model": model,
                    "source": "draft" if draft else "report",
                    "sourceSqlHash": _sql_fingerprint(original_sql),
                }
            )
        except Exception as exc:
            log.warning("Harmonisierungsmodell übersprungen: report=%s error=%s", report_ref, exc)
            skipped_reports.append({"reportRef": report_ref, "error": str(exc)})
    return profile, report_models, columns, skipped_reports


def _public_harmonization_plan(plan: dict) -> dict:
    return {
        "fieldKey": plan["fieldKey"],
        "source": plan["source"],
        "summary": plan["summary"],
        "changes": [
            {key: value for key, value in change.items() if key not in {"oldModel", "editorModel"}}
            for change in plan["changes"]
        ],
    }


@app.get("/api/reports/{report_ref}")
def get_report(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
    include_sql: bool = Query(default=False, alias="includeSql"),
) -> dict:
    profile, reports = _load_reports(config_id, project, deficiencies_only=False)
    try:
        report = find_report_by_reference(reports, report_ref)
    except LookupError as exc:
        raise _http_not_found(exc) from exc

    result = summarize_report(report)
    result["configId"] = profile.id
    result["project"] = project
    if include_sql:
        result["querySyntax"] = report.get("querySyntax") or ""
    return result



@app.get("/api/reports/{report_ref}/editor-model")
def get_editor_model(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
    prefer_draft: bool = Query(default=True, alias="preferDraft"),
) -> dict:
    profile, reports = _load_reports(config_id, project, deficiencies_only=False)
    try:
        report = find_report_by_reference(reports, report_ref)
    except LookupError as exc:
        raise _http_not_found(exc) from exc

    storage_ref = _editor_storage_ref(profile.id, project, report_ref)
    original_sql = report.get("querySyntax") or ""
    original_model = parse_editor_model(original_sql, report)
    baseline = _baseline_store().capture_if_missing(
        profile.id,
        project,
        storage_ref,
        original_sql,
        normalize_editor_model(original_model),
    )
    draft_store = _draft_store()
    draft = draft_store.get_draft(profile.id, project, storage_ref) if prefer_draft else None
    stale_draft_discarded = False
    if draft and not _editor_model_matches_report(draft.editorModel, report):
        log.warning(
            "Falsch zugeordneter Editor-Draft entfernt: config=%s project=%s report=%s draft=%s",
            profile.id,
            project,
            report_ref,
            draft.id,
        )
        draft_store.delete_draft(profile.id, project, storage_ref)
        draft = None
    if draft:
        draft, stale_draft_discarded = _discard_stale_editor_draft(
            config_id=profile.id,
            project=project,
            report_ref=storage_ref,
            current_sql=original_sql,
            current_model=original_model,
            baseline=baseline,
            draft=draft,
            draft_store=draft_store,
        )
    model = merge_missing_group_metadata(normalize_editor_model(draft.editorModel), original_model) if draft else original_model
    return {
        "configId": profile.id,
        "project": project,
        "report": summarize_report(report),
        "editorModel": model,
        "draft": draft.to_dict() if draft else None,
        "baseline": baseline.to_dict(),
        "changeLog": [change.to_dict() for change in _change_store().list_changes(profile.id, project, storage_ref)],
        "source": "draft" if draft else "imported-report-sql",
        "reportSqlHash": _sql_fingerprint(original_sql),
        "staleDraftDiscarded": stale_draft_discarded,
    }


@app.post("/api/reports/{report_ref}/restore-original")
def restore_original_report(report_ref: str, request: EditorUndoRequest) -> dict:
    try:
        profile = _store().resolve_profile(request.config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc

    storage_ref = _editor_storage_ref(profile.id, request.project, report_ref)
    baseline = _baseline_store().get_baseline(profile.id, request.project, storage_ref)
    if baseline is None:
        raise HTTPException(
            status_code=404,
            detail="Kein Ursprungsbericht gespeichert. Bitte den Bericht zuerst neu laden.",
        )

    draft_store = _draft_store()
    current_draft = draft_store.get_draft(profile.id, request.project, storage_ref)
    old_model = normalize_editor_model(current_draft.editorModel) if current_draft else baseline.editorModel
    restored_model = normalize_editor_model(baseline.editorModel)
    draft = draft_store.save_draft(
        profile.id,
        request.project,
        storage_ref,
        restored_model,
        base_sql_hash=request.base_sql_hash or _sql_fingerprint(baseline.originalSql),
    )
    change_store = _change_store()
    change = change_store.append_change(
        config_id=profile.id,
        project=request.project,
        report_ref=storage_ref,
        change_type="restore_original",
        target_path="$",
        target_label="Ursprungsbericht wiederhergestellt",
        old_value=old_model,
        new_value=restored_model,
        note=f"Ursprung vom {baseline.createdAt}",
    )
    changes = change_store.list_changes(profile.id, request.project, storage_ref)
    return {
        "configId": profile.id,
        "project": request.project,
        "reportRef": report_ref,
        "restoredChange": change.to_dict(),
        "baseline": baseline.to_dict(),
        "changes": [entry.to_dict() for entry in changes],
        "draft": draft.to_dict(),
        "editorModel": restored_model,
    }


@app.get("/api/reports/{report_ref}/draft")
def get_editor_draft(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
) -> dict:
    try:
        profile = _store().resolve_profile(config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    storage_ref = _editor_storage_ref(profile.id, project, report_ref)
    draft = _draft_store().get_draft(profile.id, project, storage_ref)
    if not draft:
        return {"exists": False, "draft": None}
    return {"exists": True, "draft": draft.to_dict(include_model=True)}


@app.put("/api/reports/{report_ref}/draft")
def save_editor_draft(report_ref: str, request: EditorDraftRequest) -> dict:
    try:
        profile = _store().resolve_profile(request.config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    model = normalize_editor_model(request.editor_model)
    model_references = _editor_model_report_references(model)
    if model_references and str(report_ref).strip().casefold() not in model_references:
        raise HTTPException(
            status_code=409,
            detail="Das Editor-Modell gehört zu einem anderen Bericht. Bitte den Bericht neu laden.",
        )
    storage_ref = _editor_storage_ref(profile.id, request.project, report_ref)
    draft = _draft_store().save_draft(
        config_id=profile.id,
        project=request.project,
        report_ref=storage_ref,
        editor_model=model,
        base_sql_hash=request.base_sql_hash,
    )
    return {
        "exists": True,
        "draft": draft.to_dict(),
        "editorModel": model,
    }


@app.delete("/api/reports/{report_ref}/draft")
def delete_editor_draft(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
) -> dict:
    try:
        profile = _store().resolve_profile(config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    storage_ref = _editor_storage_ref(profile.id, project, report_ref)
    deleted = _draft_store().delete_draft(profile.id, project, storage_ref)
    return {"deleted": deleted}

@app.get("/api/reports/{report_ref}/change-log")
def get_editor_change_log(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    try:
        profile = _store().resolve_profile(config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc
    storage_ref = _editor_storage_ref(profile.id, project, report_ref)
    changes = _change_store().list_changes(profile.id, project, storage_ref, limit=limit)
    return {
        "configId": profile.id,
        "project": project,
        "reportRef": report_ref,
        "changes": [change.to_dict() for change in changes],
    }


@app.post("/api/reports/{report_ref}/change-log", status_code=201)
def append_editor_change(report_ref: str, request: EditorChangeRequest) -> dict:
    try:
        profile = _store().resolve_profile(request.config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc

    model = normalize_editor_model(request.editor_model)
    model_references = _editor_model_report_references(model)
    if model_references and str(report_ref).strip().casefold() not in model_references:
        raise HTTPException(
            status_code=409,
            detail="Die Änderung gehört zu einem anderen Bericht. Bitte den Bericht neu laden.",
        )
    storage_ref = _editor_storage_ref(profile.id, request.project, report_ref)
    draft_store = _draft_store()
    draft = draft_store.save_draft(
        config_id=profile.id,
        project=request.project,
        report_ref=storage_ref,
        editor_model=model,
        base_sql_hash=request.base_sql_hash,
    )
    change = _change_store().append_change(
        config_id=profile.id,
        project=request.project,
        report_ref=storage_ref,
        change_type=request.change.change_type,
        target_path=request.change.target_path,
        target_label=request.change.target_label,
        old_value=request.change.old_value,
        new_value=request.change.new_value,
        note=request.change.note,
    )
    changes = _change_store().list_changes(profile.id, request.project, storage_ref)
    return {
        "configId": profile.id,
        "project": request.project,
        "reportRef": report_ref,
        "change": change.to_dict(),
        "changes": [entry.to_dict() for entry in changes],
        "draft": draft.to_dict(),
        "editorModel": model,
    }


@app.post("/api/reports/{report_ref}/change-log/undo")
def undo_editor_change(report_ref: str, request: EditorUndoRequest) -> dict:
    try:
        profile = _store().resolve_profile(request.config_id)
    except ConfigNotFoundError as exc:
        raise _http_not_found(exc) from exc

    draft_store = _draft_store()
    change_store = _change_store()
    storage_ref = _editor_storage_ref(profile.id, request.project, report_ref)
    try:
        change, model = change_store.undo_latest(draft_store, profile.id, request.project, storage_ref)
    except EditorChangeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EditorUndoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    draft = draft_store.get_draft(profile.id, request.project, storage_ref)
    changes = change_store.list_changes(profile.id, request.project, storage_ref)
    return {
        "configId": profile.id,
        "project": request.project,
        "reportRef": report_ref,
        "undoneChange": change.to_dict(),
        "changes": [entry.to_dict() for entry in changes],
        "draft": draft.to_dict() if draft else None,
        "editorModel": model,
    }

@app.post("/api/reports/{report_ref}/validate")
def validate_report_model(
    report_ref: str,
    config_id: Optional[str] = Query(default=None, alias="configId"),
    project: str = Query(default=DEFAULT_PROJECT),
) -> dict:
    profile, reports = _load_reports(config_id, project, deficiencies_only=False)
    try:
        report = find_report_by_reference(reports, report_ref)
    except LookupError as exc:
        raise _http_not_found(exc) from exc

    model = parse_editor_model(report.get("querySyntax") or "", report)
    return {
        "configId": profile.id,
        "project": project,
        "report": summarize_report(report),
        "validation": model["validation"],
        "summary": model["summary"],
    }


def _render_sql_payload(report_ref: str, request: EditorModelRequest) -> dict:
    profile, reports = _load_reports(request.config_id, request.project, deficiencies_only=False)
    try:
        report = find_report_by_reference(reports, report_ref)
    except LookupError as exc:
        raise _http_not_found(exc) from exc

    original_sql = report.get("querySyntax") or ""
    model = normalize_editor_model(request.editor_model)
    _ensure_editor_model_matches_report(model, report)
    try:
        rendered = render_sql_from_model(original_sql, model)
    except SqlGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    parsed_generated = parse_editor_model(rendered.sql, report)
    return {
        "configId": profile.id,
        "project": request.project,
        "report": summarize_report(report),
        "editorModel": model,
        "sql": rendered.sql,
        "generatedChecksSql": rendered.generated_checks_sql,
        "originalChecksSql": rendered.original_checks_sql,
        "changed": rendered.changed,
        "validation": parsed_generated["validation"],
        "summary": parsed_generated["summary"],
        "source": "generated-checks-block",
    }


@app.post("/api/reports/{report_ref}/render-sql")
def render_report_sql(report_ref: str, request: EditorModelRequest) -> dict:
    return _render_sql_payload(report_ref, request)


@app.post("/api/reports/{report_ref}/export-sql")
def export_report_sql(report_ref: str, request: EditorModelRequest) -> Response:
    payload = _render_sql_payload(report_ref, request)
    filename = _sql_export_filename(payload["report"])
    return Response(
        content=payload["sql"],
        media_type="text/sql; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export-connectors")
def get_export_connectors() -> dict:
    """List all available export connectors."""
    return {"connectors": list_connectors()}


@app.post("/api/editor/{report_ref}/export")
def export_editor_model(report_ref: str, request: EditorExportRequest) -> Response:
    """
    Export an editor model in the requested format via the connector framework.

    Body:
        editorModel: The full editor model dict
        format:      Connector name, e.g. "mssql", "json", "infozoom"
        options:     Format-specific options dict

    Returns a file download response with warnings embedded in the content.
    """
    try:
        connector = get_connector(request.format)
    except KeyError:
        available = ", ".join(c["name"] for c in list_connectors())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown export format '{request.format}'. Available: {available}",
        )

    model = normalize_editor_model(dict(request.editor_model))

    try:
        warnings = connector.validate(model)
        content = connector.export(model, options=dict(request.options))
    except ExportConnectorError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Build download filename from report info
    report = model.get("report") or {}
    raw_name = (
        report.get("internalName")
        or report.get("displayName")
        or report.get("id")
        or report_ref
        or "nemo_export"
    )
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", str(raw_name)).strip("._") or "nemo_export"
    ext = connector.file_extension
    filename = f"{stem}.{ext}" if not stem.lower().endswith(f".{ext}") else stem

    # Choose media type by format
    media_types = {
        "json": "application/json; charset=utf-8",
        "mssql": "text/sql; charset=utf-8",
        "infozoom": "text/plain; charset=utf-8",
    }
    media_type = media_types.get(request.format, "text/plain; charset=utf-8")

    # Encode as bytes (UTF-8)
    content_bytes = content.encode("utf-8")

    groups = ((model.get("checks") or {}).get("groups") or [])
    all_rules = [r for g in groups for r in (g.get("rules") or [])]

    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-Export-Format": request.format,
        "X-Export-Warnings": str(len(warnings)),
        "X-Export-Total-Rules": str(len(all_rules)),
    }

    return Response(
        content=content_bytes,
        media_type=media_type,
        headers=response_headers,
    )


@app.post("/api/reports/{report_ref}/write-to-nemo")
def write_report_to_nemo(report_ref: str, request: NemoReportWriteRequest) -> dict:
    operation_id = request_id_context.get() or uuid.uuid4().hex[:12]
    log.info(
        "[%s] NEMO write startet: report_ref=%s config=%s project=%s",
        operation_id,
        report_ref,
        request.config_id or "default",
        request.project,
    )
    payload = _render_sql_payload(report_ref, request)
    errors = [
        finding
        for finding in (payload.get("validation") or {}).get("findings", [])
        if str(finding.get("severity") or "").casefold() == "error"
    ]
    if errors:
        raise HTTPException(status_code=422, detail="Das generierte SQL enthält Validierungsfehler und wurde nicht nach NEMO geschrieben.")

    with _nemo_for_config(request.config_id) as (profile, nemo):
        reports = get_reports(nemo=nemo, project=request.project, filter_value="*")
        try:
            report = find_report_by_reference(reports, report_ref)
        except LookupError as exc:
            raise _http_not_found(exc) from exc

        internal_name = str(report.get("internalName") or "").strip()
        if not internal_name:
            raise HTTPException(status_code=409, detail="Der bestehende NEMO-Bericht hat keinen Internalname.")
        if request.overwrite_confirmation.strip() != internal_name:
            raise HTTPException(status_code=409, detail="Die Überschreib-Bestätigung stimmt nicht mit dem Bericht überein.")

        exact_matches = [
            item
            for item in reports
            if str(item.get("internalName") or "").strip().casefold() == internal_name.casefold()
        ]
        if len(exact_matches) != 1:
            raise HTTPException(status_code=409, detail="Der NEMO-Bericht ist über den Internalname nicht eindeutig vorhanden.")

        current_report = exact_matches[0]
        current_is_top_25 = _has_top_25_suffix(current_report)
        if current_is_top_25:
            top_25_report = current_report
            top_25_created = False
            top_25_strategy = "selected-top-25"
        else:
            top_25_report, top_25_created, top_25_strategy = _resolve_top_25_report(reports, current_report)
        log.info(
            "[%s] TOP-25-Auflösung: strategy=%s created=%s source=%s target=%s",
            operation_id,
            top_25_strategy,
            top_25_created,
            internal_name,
            top_25_report.get("internalName"),
        )
        try:
            top_25_sql = render_top_25_sql(payload["sql"])
        except SqlGenerationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        updates = [(current_report, top_25_sql if current_is_top_25 else payload["sql"])]
        if not current_is_top_25:
            updates.append((top_25_report, top_25_sql))

        baseline_store = _baseline_store()
        for existing_report, _new_sql in updates:
            if top_25_created and existing_report is top_25_report:
                continue
            existing_sql = str(existing_report.get("querySyntax") or "")
            baseline_store.capture_if_missing(
                profile.id,
                request.project,
                str(existing_report.get("id") or existing_report.get("internalName") or ""),
                existing_sql,
                normalize_editor_model(parse_editor_model(existing_sql, existing_report)),
            )

        try:
            log.info(
                "[%s] NEMO write sendet Berichte: %s",
                operation_id,
                [report.get("internalName") for report, _sql in updates],
            )
            update_reports_sql(nemo=nemo, project=request.project, updates=updates)
        except ReportTenantMismatchError as exc:
            log.warning("[%s] Tenant-Sperre: %s", operation_id, exc)
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            log.exception(
                "[%s] NEMO-Berichte konnten nicht aktualisiert werden: %s",
                operation_id,
                internal_name,
            )
            error_summary = _nemo_error_summary(exc)
            raise HTTPException(
                status_code=502,
                detail=f"NEMO hat das gemeinsame Berichtsupdate abgelehnt: {error_summary}. Vorgang: {operation_id}",
            ) from exc

    log.info(
        "[%s] NEMO write erfolgreich: reports=%s",
        operation_id,
        [report.get("internalName") for report, _sql in updates],
    )

    return {
        "status": "updated",
        "operationId": operation_id,
        "configId": profile.id,
        "project": request.project,
        "report": payload["report"],
        "internalName": internal_name,
        "changed": payload["changed"],
        "top25Created": top_25_created,
        "updatedReports": [summarize_report(report) for report, _sql in updates],
    }


def _has_top_25_suffix(report: dict) -> bool:
    display_name = str(report.get("displayName") or "").strip()
    internal_name = str(report.get("internalName") or "").strip()
    return bool(re.search(r"(?i)(?:\s+|_)TOP(?:\s+|_)25$", display_name)) or bool(
        re.search(r"(?i)_TOP_25$", internal_name)
    )


def _nemo_error_summary(exc: Exception) -> str:
    text = str(exc or "")
    match = re.search(r"Status:\s*\d+\s*,\s*error:\s*(.+)\s*$", text, re.DOTALL | re.IGNORECASE)
    raw_error = match.group(1).strip() if match else ""
    if raw_error:
        try:
            payload = json.loads(raw_error)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            extensions = payload.get("Extensions") or {}
            raw_error = str(
                payload.get("Detail")
                or payload.get("message")
                or (extensions.get("message") if isinstance(extensions, dict) else "")
                or payload.get("Title")
                or raw_error
            )
    summary = re.sub(r"\s+", " ", raw_error).strip()
    return summary[:300] if summary else type(exc).__name__


def _resolve_top_25_report(reports: list[dict], source_report: dict) -> tuple[dict, bool, str]:
    display_name = str(source_report.get("displayName") or "").strip()
    internal_name = str(source_report.get("internalName") or "").strip()
    wanted_display = f"{display_name} TOP 25".casefold()
    wanted_internal = f"{internal_name}_top_25".casefold()
    exact_matches = [
        report
        for report in reports
        if str(report.get("displayName") or "").strip().casefold() == wanted_display
        or str(report.get("internalName") or "").strip().casefold() == wanted_internal
    ]
    unique_matches = _unique_reports(exact_matches)
    if len(unique_matches) == 1:
        return next(iter(unique_matches.values())), False, "exact"
    if len(unique_matches) != 1:
        if unique_matches:
            raise HTTPException(status_code=409, detail="Der zugehörige TOP-25-Bericht ist in NEMO nicht eindeutig.")

    source_keys = _report_subject_keys(source_report)
    translated_matches = [
        report
        for report in reports
        if _has_top_25_suffix(report) and source_keys.intersection(_report_subject_keys(report))
    ]
    unique_matches = _unique_reports(translated_matches)
    if len(unique_matches) == 1:
        return next(iter(unique_matches.values())), False, "translated"
    if len(unique_matches) > 1:
        raise HTTPException(
            status_code=409,
            detail="Der zugehörige TOP-25-Bericht ist über deutsche/englische Bezeichnungen nicht eindeutig.",
        )
    return _build_top_25_report(source_report), True, "created"


def _unique_reports(reports: list[dict]) -> dict[str, dict]:
    return {
        str(report.get("id") or report.get("internalName") or id(report)): report
        for report in reports
    }


def _report_subject_keys(report: dict) -> set[str]:
    values = [report.get("displayName"), report.get("internalName")]
    translations = report.get("displayNameTranslations") or {}
    if isinstance(translations, dict):
        values.extend(translations.values())
    return {key for value in values if (key := _normalize_report_subject(value))}


def _normalize_report_subject(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character)).casefold()
    text = re.sub(r"\btop[\s_-]*25\b", " ", text)
    tokens = re.findall(r"[a-z0-9]+", text)
    aliases = {
        "customer": "customer", "customers": "customer", "kunde": "customer", "kunden": "customer",
        "supplier": "supplier", "suppliers": "supplier", "lieferant": "supplier", "lieferanten": "supplier",
        "part": "part", "parts": "part", "teil": "part", "teile": "part",
        "address": "address", "addresses": "address", "adresse": "address", "adressen": "address",
        "contact": "contact", "contacts": "contact", "kontakt": "contact", "kontakte": "contact",
    }
    ignored = {"deficiencies", "deficiency"}
    normalized = [aliases.get(token, token) for token in tokens if token not in ignored]
    return " ".join(normalized)


def _build_top_25_report(source_report: dict) -> dict:
    display_name = re.sub(
        r"(?i)(?:\s+|_)TOP(?:\s+|_)25$",
        "",
        str(source_report.get("displayName") or "").strip(),
    )
    internal_name = re.sub(
        r"(?i)_TOP_25$",
        "",
        str(source_report.get("internalName") or "").strip(),
    )
    if not display_name or not internal_name:
        raise HTTPException(status_code=409, detail="Der TOP-25-Bericht kann ohne Displayname und Internalname nicht erstellt werden.")

    translations = source_report.get("displayNameTranslations") or {}
    translated_names = {
        str(language): f"{str(name).strip()} TOP 25"
        for language, name in translations.items()
        if str(name).strip()
    } if isinstance(translations, dict) else {}
    created = dict(source_report)
    created.update(
        {
            "id": "",
            "displayName": f"{display_name} TOP 25",
            "internalName": f"{internal_name}_top_25",
            "displayNameTranslations": translated_names,
            "querySyntax": "",
            "isCustom": True,
        }
    )
    return created


def _sql_export_filename(report: dict) -> str:
    raw_name = report.get("internalName") or report.get("displayName") or report.get("id") or "nemo_report"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", str(raw_name)).strip("._")
    filename = stem or "nemo_report"
    return filename if filename.lower().endswith(".sql") else f"{filename}.sql"

@app.post("/api/reports/{report_ref}/run")
def run_report(report_ref: str, request: ReportRunRequest) -> dict:
    with _nemo_for_config(request.config_id) as (profile, nemo):
        reports = get_reports(nemo=nemo, project=request.project, filter_value="*")
        try:
            report = find_report_by_reference(reports, report_ref)
        except LookupError as exc:
            raise _http_not_found(exc) from exc
        preview = run_report_preview(
            nemo=nemo,
            project=request.project,
            report=report,
            max_rows=request.max_rows,
        )

    return {
        "configId": profile.id,
        "project": request.project,
        "report": summarize_report(report),
        "preview": preview,
    }
