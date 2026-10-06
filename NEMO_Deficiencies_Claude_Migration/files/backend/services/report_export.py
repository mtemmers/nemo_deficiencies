import os
import re
from pathlib import Path
from typing import Any

from nemo_library import NemoLibrary

from backend.services.report_service import export_report_data
from backend.services.report_utils import (
    select_reports,
    write_index_csv,
    write_json,
    write_report_sql_files,
)


class ReportExportError(RuntimeError):
    pass


def default_export_directory() -> Path:
    documents = Path.home() / "Documents"
    return documents / "NEMO Deficiencies Exports"


def resolve_export_directory(value: str) -> Path:
    raw = value.strip()
    if not raw:
        return default_export_directory().resolve()
    expanded = os.path.expandvars(os.path.expanduser(raw))
    return Path(expanded).resolve()


def tenant_export_directory(base_dir: Path, tenant: str) -> Path:
    segment = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", tenant.strip())
    segment = re.sub(r"_+", "_", segment)
    segment = re.sub(r"\s+", " ", segment).strip(" ._")
    if not segment:
        segment = "tenant"
    if segment.casefold() in {
        "con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5",
        "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5",
        "lpt6", "lpt7", "lpt8", "lpt9",
    }:
        segment = f"_{segment}"
    return base_dir / segment


def export_reports(
    *,
    nemo: NemoLibrary,
    project: str,
    all_reports: list[dict[str, Any]],
    report_refs: list[str],
    contains_values: list[str],
    output_dir: Path,
    export_data: bool,
    refresh_index: bool,
    separator: str = ";",
    encoding: str = "utf-8-sig",
) -> dict[str, Any]:
    selected_reports = select_reports(
        reports=all_reports,
        exact_values=report_refs,
        contains_values=contains_values,
    )
    if not selected_reports:
        raise ReportExportError("Keine passenden Berichte gefunden.")

    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_reports = all_reports if refresh_index else selected_reports
    sql_reports = catalog_reports if refresh_index else selected_reports
    sql_files = write_report_sql_files(
        reports=sql_reports,
        sql_dir=output_dir / "sql",
        encoding=encoding,
    )

    data_files: dict[int, str] = {}
    data_shapes: dict[int, tuple[int, int]] = {}
    data_errors: dict[int, str] = {}
    if export_data:
        data_files, data_shapes, data_errors = export_report_data(
            nemo=nemo,
            project=project,
            reports=selected_reports,
            data_dir=output_dir / "data",
            separator=separator,
            encoding=encoding,
        )

    metadata_path = output_dir / "reports_metadata.json"
    index_path = output_dir / "reports_index.csv"
    catalog_matches_selection = catalog_reports is selected_reports
    write_json(metadata_path, catalog_reports)
    write_index_csv(
        path=index_path,
        reports=catalog_reports,
        sql_files=sql_files,
        data_files=data_files if catalog_matches_selection else {},
        data_shapes=data_shapes if catalog_matches_selection else {},
        data_errors=data_errors if catalog_matches_selection else {},
        separator=separator,
        encoding=encoding,
    )

    return {
        "outputDir": str(output_dir),
        "selectedReportCount": len(selected_reports),
        "catalogReportCount": len(catalog_reports),
        "sqlFileCount": len(sql_files),
        "dataFileCount": len(data_files),
        "dataErrorCount": len(data_errors),
        "indexFile": str(index_path),
        "metadataFile": str(metadata_path),
    }
