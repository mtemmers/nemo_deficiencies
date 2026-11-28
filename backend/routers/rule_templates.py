from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["rule-templates"])

DEFAULT_PROJECT = "Master Data"


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


class RuleCatalogAnalysisRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_id: Optional[str] = Field(default=None, alias="configId")
    project: str = Field(default=DEFAULT_PROJECT, pattern=r"^Master Data$")


class RuleCatalogImportRequest(RuleCatalogAnalysisRequest):
    candidate_keys: list[str] = Field(alias="candidateKeys", min_length=1, max_length=5000)


class RuleCatalogCandidateDecisionRequest(RuleCatalogAnalysisRequest):
    candidate_key: str = Field(alias="candidateKey", min_length=1, max_length=240)
    decision: str = Field(pattern=r"^(rejected|pending)$")


@router.get("/api/rule-catalog")
def rule_catalog() -> dict:
    from backend import main as m

    return m.get_rule_catalog()


@router.get("/api/rule-templates")
def list_rule_templates(
    status: Optional[str] = Query(default=None, pattern=r"^(draft|approved|deprecated)$"),
) -> dict:
    from backend import main as m

    templates = m._rule_template_store().list_templates(status=status)
    return {"count": len(templates), "templates": [template.to_dict() for template in templates]}


@router.post("/api/rule-templates/analyze-existing")
def analyze_existing_rule_templates(request: RuleCatalogAnalysisRequest) -> dict:
    from backend import main as m

    profile, report_models, _columns, skipped_reports = m._load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = m._rule_template_store()
    analysis = m.analyze_rule_catalog_candidates(
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


@router.post("/api/rule-templates/import-existing")
def import_existing_rule_templates(request: RuleCatalogImportRequest) -> dict:
    from backend import main as m

    profile, report_models, _columns, skipped_reports = m._load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = m._rule_template_store()
    analysis = m.analyze_rule_catalog_candidates(report_models, store.list_templates())
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
        except (m.RuleCatalogError, m.RuleTemplateValidationError) as exc:
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


@router.post("/api/rule-templates/candidate-decisions")
def set_rule_template_candidate_decision(request: RuleCatalogCandidateDecisionRequest) -> dict:
    from backend import main as m

    profile, report_models, _columns, _skipped_reports = m._load_harmonization_context(
        request.config_id,
        request.project,
    )
    store = m._rule_template_store()
    analysis = m.analyze_rule_catalog_candidates(report_models, store.list_templates())
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


@router.get("/api/rule-templates/{template_ref}")
def get_rule_template(
    template_ref: str,
    version: Optional[int] = Query(default=None, ge=1),
) -> dict:
    from backend import main as m

    try:
        template = m._rule_template_store().get_template(template_ref, version=version)
    except m.RuleTemplateNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    return {"template": template.to_dict()}


@router.post("/api/rule-templates", status_code=201)
def create_rule_template(request: RuleTemplateCreateRequest) -> dict:
    from backend import main as m

    try:
        template = m._rule_template_store().create_template(
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
    except (m.RuleCatalogError, m.RuleTemplateValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@router.post("/api/rule-templates/{template_ref}/versions", status_code=201)
def create_rule_template_version(template_ref: str, request: RuleTemplateVersionRequest) -> dict:
    from backend import main as m

    try:
        template = m._rule_template_store().add_version(
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
    except m.RuleTemplateNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except (m.RuleCatalogError, m.RuleTemplateValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@router.patch("/api/rule-templates/{template_ref}")
def update_rule_template_metadata(template_ref: str, request: RuleTemplateMetadataRequest) -> dict:
    from backend import main as m

    try:
        template = m._rule_template_store().update_metadata(
            template_ref,
            name=request.name,
            description=request.description,
            status=request.status,
        )
    except m.RuleTemplateNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except m.RuleCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict()}


@router.post("/api/rule-templates/{template_ref}/resolve")
def resolve_catalog_rule(template_ref: str, request: RuleTemplateResolveRequest) -> dict:
    from backend import main as m

    try:
        template = m._rule_template_store().get_template(template_ref, version=request.version)
        resolved = m.resolve_rule_template(
            template.version,
            field=request.field,
            display_name=request.display_name,
            description=request.description,
            parameters=request.parameters,
        )
    except m.RuleTemplateNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except (m.RuleTemplateValidationError, m.RuleTemplateResolutionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"template": template.to_dict(), "resolvedRule": resolved.to_dict()}


@router.post("/api/rule-template-bindings", status_code=201)
def bind_catalog_rule(request: RuleTemplateBindingRequest) -> dict:
    from backend import main as m

    try:
        binding = m._rule_template_store().bind_rule(
            template_ref=request.template_id,
            template_version=request.template_version,
            config_id=request.config_id,
            project=request.project,
            report_ref=request.report_ref,
            group_ref=request.group_ref,
            rule_ref=request.rule_ref,
            parameters=request.parameters,
        )
    except m.RuleTemplateNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except m.RuleCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"binding": binding.to_dict()}


# /api/editor-model/validate stays in backend/main.py because EditorModelRequest is defined there.
