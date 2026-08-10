import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import uuid4

import requests
from nemo_library import NemoLibrary
from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.model.report import Report

from backend.services.report_utils import report_to_dict, sort_reports


log = logging.getLogger(__name__)


class ReportTenantMismatchError(ValueError):
    pass


def create_nemo_client(config_path: Path) -> NemoLibrary:
    return NemoLibrary(config_file=str(config_path))


def _metadata_value(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def column_to_dict(column: Any) -> Dict[str, Any]:
    return {
        "id": _metadata_value(column, "id") or "",
        "displayName": _metadata_value(column, "displayName") or "",
        "internalName": _metadata_value(column, "internalName") or "",
        "importName": _metadata_value(column, "importName") or "",
        "description": _metadata_value(column, "description") or "",
        "dataType": _metadata_value(column, "dataType") or "",
        "columnType": _metadata_value(column, "columnType") or "",
        "parentAttributeGroupInternalName": _metadata_value(column, "parentAttributeGroupInternalName") or "",
    }


def get_columns(nemo: NemoLibrary, project: str, filter_value: str = "*") -> List[Dict[str, Any]]:
    columns_raw = nemo.getColumns(projectname=project, filter=filter_value)
    columns = [column_to_dict(column) for column in columns_raw]
    return sorted(
        columns,
        key=lambda column: (
            (column.get("displayName") or column.get("internalName") or "").casefold(),
            (column.get("internalName") or "").casefold(),
        ),
    )


def get_reports(nemo: NemoLibrary, project: str, filter_value: str = "*") -> List[Dict[str, Any]]:
    reports_raw = nemo.getReports(projectname=project, filter=filter_value)
    return sort_reports(report_to_dict(report) for report in reports_raw)


def load_report_dataframe(nemo: NemoLibrary, project: str, report: Dict[str, Any]) -> Any:
    report_id = report.get("id")
    if report_id:
        return nemo.LoadReport(projectname=project, report_guid=report_id)

    display_name = report.get("displayName")
    if display_name:
        return nemo.LoadReport(projectname=project, report_name=display_name)

    internal_name = report.get("internalName")
    raise ValueError(f"Report ohne id/displayName kann nicht geladen werden: {internal_name}")


def load_project_field_values(
    nemo: NemoLibrary,
    project: str,
    source_column_name: str,
    max_rows: int = 500,
) -> List[Any]:
    safe_rows = max(10, min(int(max_rows), 1000))
    token = uuid4().hex
    report_internal_name = f"nemo_deficiencies_field_profile_{token}"
    report_display_name = f"(SYSTEM) NEMO Deficiencies Field Profile {token[:8]}"
    field_reference = _hana_identifier(source_column_name)
    query = (
        f'SELECT TOP {safe_rows} TO_NVARCHAR({field_reference}) AS "FIELD_VALUE" '
        'FROM $schema.$table'
    )
    temporary_report = Report(
        displayName=report_display_name,
        internalName=report_internal_name,
        description="Temporary one-column profile; automatically deleted.",
        querySyntax=query,
        isCustom=True,
    )
    report_id = ""
    report_created = False
    cleanup_error: Exception | None = None
    try:
        log.info(
            "Temporärer Feldprofil-Report wird erstellt: project=%s report=%s field=%s rows=%s",
            project,
            report_internal_name,
            source_column_name,
            safe_rows,
        )
        nemo.createReports(projectname=project, reports=[temporary_report])
        report_created = True
        reports = get_reports(nemo=nemo, project=project, filter_value="*")
        created = next(
            (report for report in reports if str(report.get("internalName") or "") == report_internal_name),
            None,
        )
        if not created or not created.get("id"):
            raise RuntimeError("Der temporäre NEMO-Feldprofil-Report wurde nicht gefunden.")
        report_id = str(created["id"])
        dataframe = nemo.LoadReport(projectname=project, report_guid=report_id)
        if dataframe is None or dataframe.empty:
            return []
        return dataframe.iloc[:, 0].tolist()
    finally:
        if report_created and not report_id:
            try:
                reports = get_reports(nemo=nemo, project=project, filter_value="*")
                created = next(
                    (
                        report for report in reports
                        if str(report.get("internalName") or "") == report_internal_name
                    ),
                    None,
                )
                report_id = str(created.get("id") or "") if created else ""
            except Exception as exc:
                cleanup_error = exc
        if report_id:
            try:
                nemo.deleteReports(reports=[report_id])
                log.info("Temporärer Feldprofil-Report gelöscht: report=%s", report_internal_name)
            except Exception as exc:  # cleanup must be visible to the caller and logs
                cleanup_error = exc
                log.exception("Temporärer Feldprofil-Report konnte nicht gelöscht werden: report=%s", report_internal_name)
        elif report_created and cleanup_error is None:
            cleanup_error = RuntimeError(
                f"Der temporäre Feldprofil-Report '{report_internal_name}' wurde zur Bereinigung nicht gefunden."
            )
        if cleanup_error:
            raise RuntimeError(
                f"Der temporäre Feldprofil-Report '{report_internal_name}' konnte nicht gelöscht werden."
            ) from cleanup_error


def _hana_identifier(value: str) -> str:
    name = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or len(name) > 240:
        raise ValueError("Ungültiger Feldname für die Profilabfrage.")
    return name


def update_report_sql(nemo: NemoLibrary, project: str, report: Dict[str, Any], sql: str) -> None:
    update_reports_sql(nemo, project, [(report, sql)])


def update_reports_sql(
    nemo: NemoLibrary,
    project: str,
    updates: List[Tuple[Dict[str, Any], str]],
) -> None:
    if not updates:
        raise ValueError("Mindestens ein NEMO-Bericht muss aktualisiert werden.")
    updated_reports = [_updated_report(report, sql) for report, sql in updates]
    internal_names = [report.internalName.casefold() for report in updated_reports]
    if len(internal_names) != len(set(internal_names)):
        raise ValueError("Ein NEMO-Bericht ist im gemeinsamen Update mehrfach enthalten.")
    current_tenant = str(nemo.config.get_tenant() or "").strip()
    mismatched_reports = [
        source_report
        for source_report, _sql in updates
        if source_report.get("id")
        and source_report.get("isCustom") is True
        and str(source_report.get("tenant") or "").strip()
        and current_tenant
        and str(source_report.get("tenant") or "").strip().casefold() != current_tenant.casefold()
    ]
    if mismatched_reports:
        source_tenants = sorted(
            {str(report.get("tenant") or "").strip() for report in mismatched_reports},
            key=str.casefold,
        )
        report_names = ", ".join(str(report.get("internalName") or report.get("id")) for report in mismatched_reports)
        raise ReportTenantMismatchError(
            f"Keine Berichte geändert: Die ausgewählte Konfiguration gehört zum Tenant '{current_tenant}', "
            f"aber {report_names} gehört zu '{', '.join(source_tenants)}'. Bitte die passende Konfiguration auswählen."
        )

    regular_reports: List[Report] = []
    for (source_report, _sql), updated_report in zip(updates, updated_reports):
        if source_report.get("id") and source_report.get("isCustom") is False:
            _create_customized_report(nemo, project, updated_report)
        else:
            regular_reports.append(updated_report)

    if regular_reports:
        log.info(
            "NEMO createReports startet: project=%s reports=%s",
            project,
            [report.internalName for report in regular_reports],
        )
        nemo.createReports(projectname=project, reports=regular_reports)
        log.info(
            "NEMO createReports erfolgreich: project=%s reports=%s",
            project,
            [report.internalName for report in regular_reports],
        )


def _create_customized_report(nemo: NemoLibrary, project: str, report: Report) -> None:
    config = nemo.config
    report.id = ""
    report.projectId = getProjectID(config, project)
    report.tenant = config.get_tenant()
    report.isCustom = True
    log.info(
        "NEMO Custom-Report wird erstellt: project=%s report=%s",
        project,
        report.internalName,
    )
    response = requests.post(
        f"{config.get_config_nemo_url()}/api/nemo-persistence/metadata/Reports",
        json=report.to_dict(),
        headers=config.connection_get_headers(),
        params={"translationHandling": "UseAuxiliaryTranslationFields"},
        timeout=60,
    )
    if response.status_code != 201:
        raise ValueError(
            f"POST customized Report failed. Status: {response.status_code}, error: {response.text}"
        )
    log.info(
        "NEMO Custom-Report erfolgreich erstellt: project=%s report=%s",
        project,
        report.internalName,
    )


def _updated_report(report: Dict[str, Any], sql: str) -> Report:
    internal_name = str(report.get("internalName") or "").strip()
    display_name = str(report.get("displayName") or "").strip()
    if not internal_name or not display_name:
        raise ValueError("Der NEMO-Bericht benötigt Displayname und Internalname für ein Update.")
    if not str(sql or "").strip():
        raise ValueError("Leeres SQL kann nicht nach NEMO geschrieben werden.")

    return Report(
        columns=list(report.get("columns") or []),
        description=str(report.get("description") or ""),
        descriptionTranslations=dict(report.get("descriptionTranslations") or {}),
        displayName=display_name,
        displayNameTranslations=dict(report.get("displayNameTranslations") or {}),
        internalName=internal_name,
        querySyntax=sql,
        reportCategories=list(report.get("reportCategories") or []),
        id=str(report.get("id") or ""),
        projectId=str(report.get("projectId") or ""),
        tenant=str(report.get("tenant") or ""),
        isCustom=bool(report.get("isCustom")),
        metadataClassificationInternalName=str(report.get("metadataClassificationInternalName") or ""),
    )
