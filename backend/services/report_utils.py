import csv
import json
import re
import unicodedata
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFICIENCIES_PREFIX = "(DEFICIENCIES)"


def report_to_dict(report: Any) -> Dict[str, Any]:
    if isinstance(report, dict):
        return dict(report)
    if hasattr(report, "to_dict") and callable(report.to_dict):
        return report.to_dict()
    if is_dataclass(report):
        return asdict(report)

    keys = (
        "id",
        "projectId",
        "tenant",
        "displayName",
        "internalName",
        "description",
        "querySyntax",
        "columns",
        "reportCategories",
        "displayNameTranslations",
        "descriptionTranslations",
    )
    return {key: getattr(report, key) for key in keys if hasattr(report, key)}


def sort_reports(reports: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        reports,
        key=lambda item: (item.get("displayName") or item.get("internalName") or "").casefold(),
    )


def is_deficiency_report(report: Dict[str, Any], prefix: str = DEFICIENCIES_PREFIX) -> bool:
    name = (report.get("displayName") or report.get("internalName") or "").strip()
    return name.casefold().startswith(prefix.casefold())


def filter_deficiency_reports(
    reports: Iterable[Dict[str, Any]],
    prefix: str = DEFICIENCIES_PREFIX,
) -> List[Dict[str, Any]]:
    return [report for report in reports if is_deficiency_report(report, prefix)]


def is_top_25_report(report: Dict[str, Any]) -> bool:
    for value in (
        report.get("displayName"),
        report.get("internalName"),
    ):
        if value and re.search(r"(?:\s+|_)TOP(?:\s+|_)25$", str(value).strip(), re.IGNORECASE):
            return True
    return False


def filter_primary_deficiency_reports(
    reports: Iterable[Dict[str, Any]],
    prefix: str = DEFICIENCIES_PREFIX,
) -> List[Dict[str, Any]]:
    return [
        report
        for report in filter_deficiency_reports(reports, prefix)
        if not is_top_25_report(report)
    ]


def read_report_file(path: Path) -> List[str]:
    values: List[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            values.append(value)
    return values


def report_identifiers(report: Dict[str, Any]) -> List[str]:
    return [
        str(value).casefold()
        for value in (
            report.get("displayName"),
            report.get("internalName"),
            report.get("id"),
        )
        if value
    ]


def select_reports(
    reports: List[Dict[str, Any]],
    exact_values: List[str],
    contains_values: List[str],
) -> List[Dict[str, Any]]:
    exact = {value.strip().casefold() for value in exact_values if value.strip()}
    contains = [value.strip().casefold() for value in contains_values if value.strip()]
    if not exact and not contains:
        return reports

    selected: List[Dict[str, Any]] = []
    for report in reports:
        identifiers = report_identifiers(report)
        is_exact_match = bool(exact.intersection(identifiers))
        is_contains_match = any(
            needle in identifier
            for needle in contains
            for identifier in identifiers[:2]
        )
        if is_exact_match or is_contains_match:
            selected.append(report)
    return selected


def normalize_filename(value: Optional[str], fallback: str) -> str:
    text = (value or fallback).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", text)
    text = re.sub(r"\s+", " ", text).strip(" ._")
    return (text or fallback)[:120]


def unique_report_paths(
    reports: Iterable[Dict[str, Any]],
    base_dir: Path,
    suffix: str,
) -> List[Path]:
    seen: Dict[str, int] = {}
    paths: List[Path] = []

    for index, report in enumerate(reports, start=1):
        preferred_name = report.get("displayName") or report.get("internalName")
        base_name = normalize_filename(preferred_name, f"report_{index:03d}")
        name_key = base_name.casefold()
        seen[name_key] = seen.get(name_key, 0) + 1

        if seen[name_key] > 1:
            filename = f"{index:03d}_{base_name}_{seen[name_key]}{suffix}"
        else:
            filename = f"{index:03d}_{base_name}{suffix}"
        paths.append(base_dir / filename)

    return paths


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report_sql_files(
    reports: List[Dict[str, Any]],
    sql_dir: Path,
    encoding: str,
) -> Dict[int, str]:
    sql_dir.mkdir(parents=True, exist_ok=True)
    sql_paths = unique_report_paths(reports, sql_dir, ".sql")
    written: Dict[int, str] = {}

    for index, (report, sql_path) in enumerate(zip(reports, sql_paths)):
        query = report.get("querySyntax") or ""
        if not query.strip():
            continue
        sql_path.write_text(query.rstrip() + "\n", encoding=encoding)
        written[index] = str(sql_path)

    return written


def write_index_csv(
    path: Path,
    reports: List[Dict[str, Any]],
    sql_files: Dict[int, str],
    data_files: Dict[int, str],
    data_shapes: Dict[int, Tuple[int, int]],
    data_errors: Dict[int, str],
    separator: str,
    encoding: str,
) -> None:
    fieldnames = [
        "nr",
        "displayName",
        "internalName",
        "id",
        "description",
        "reportCategories",
        "columns",
        "hasQuerySyntax",
        "sqlFile",
        "dataFile",
        "rows",
        "columnsCount",
        "dataExportError",
    ]

    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=separator)
        writer.writeheader()
        for index, report in enumerate(reports):
            rows, columns_count = data_shapes.get(index, ("", ""))
            writer.writerow(
                {
                    "nr": index + 1,
                    "displayName": report.get("displayName") or "",
                    "internalName": report.get("internalName") or "",
                    "id": report.get("id") or "",
                    "description": report.get("description") or "",
                    "reportCategories": "|".join(report.get("reportCategories") or []),
                    "columns": "|".join(report.get("columns") or []),
                    "hasQuerySyntax": bool((report.get("querySyntax") or "").strip()),
                    "sqlFile": sql_files.get(index, ""),
                    "dataFile": data_files.get(index, ""),
                    "rows": rows,
                    "columnsCount": columns_count,
                    "dataExportError": data_errors.get(index, ""),
                }
            )
