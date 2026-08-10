import csv
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from nemo_library import NemoLibrary

from backend.services.nemo_client import load_report_dataframe
from backend.services.report_utils import unique_report_paths

log = logging.getLogger(__name__)


def summarize_report(report: Dict[str, Any]) -> Dict[str, Any]:
    columns = report.get("columns") or []
    return {
        "id": report.get("id") or "",
        "displayName": report.get("displayName") or "",
        "internalName": report.get("internalName") or "",
        "description": report.get("description") or "",
        "reportCategories": report.get("reportCategories") or [],
        "columnsCount": len(columns),
        "hasQuerySyntax": bool((report.get("querySyntax") or "").strip()),
    }


def find_report_by_reference(reports: List[Dict[str, Any]], report_ref: str) -> Dict[str, Any]:
    wanted = report_ref.strip().casefold()
    for report in reports:
        identifiers = (
            report.get("id"),
            report.get("displayName"),
            report.get("internalName"),
        )
        if wanted in {str(value).casefold() for value in identifiers if value}:
            return report
    raise LookupError(f"Report nicht gefunden: {report_ref}")


def _jsonable_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value
    if hasattr(value, "item"):
        return _jsonable_value(value.item())
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def dataframe_preview(df: Any, max_rows: int) -> Dict[str, Any]:
    preview = df.head(max_rows)
    rows = [
        {column: _jsonable_value(value) for column, value in row.items()}
        for row in preview.to_dict(orient="records")
    ]
    return {
        "columns": [str(column) for column in df.columns],
        "rowCount": int(len(df)),
        "returnedRows": len(rows),
        "rows": rows,
    }


def run_report_preview(
    nemo: NemoLibrary,
    project: str,
    report: Dict[str, Any],
    max_rows: int,
) -> Dict[str, Any]:
    df = load_report_dataframe(nemo, project, report)
    return dataframe_preview(df, max_rows=max_rows)


def export_report_data(
    nemo: NemoLibrary,
    project: str,
    reports: List[Dict[str, Any]],
    data_dir: Path,
    separator: str,
    encoding: str,
) -> Tuple[Dict[int, str], Dict[int, Tuple[int, int]], Dict[int, str]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_paths = unique_report_paths(reports, data_dir, ".csv")
    exported: Dict[int, str] = {}
    shapes: Dict[int, Tuple[int, int]] = {}
    errors: Dict[int, str] = {}

    for index, (report, csv_path) in enumerate(zip(reports, csv_paths)):
        name = report.get("displayName") or report.get("internalName") or f"Report {index + 1}"
        try:
            log.info("Lade Reportdaten: %s", name)
            df = load_report_dataframe(nemo, project, report)
            df.to_csv(
                csv_path,
                sep=separator,
                encoding=encoding,
                index=False,
                quoting=csv.QUOTE_ALL,
            )
            exported[index] = str(csv_path)
            shapes[index] = (len(df), len(df.columns))
            log.info("OK: %s -> %s Zeilen, %s Spalten", name, len(df), len(df.columns))
        except Exception as exc:
            errors[index] = f"{type(exc).__name__}: {exc}"
            log.error("Fehler beim Datenexport fuer %s: %s", name, exc)

    return exported, shapes, errors
