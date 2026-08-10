import hashlib
import json
import re
from collections import Counter
from copy import deepcopy
from typing import Any, Dict, Iterable

from backend.services.sql_model import normalize_editor_model


class HarmonizationError(ValueError):
    pass


def build_harmonization_matrix(
    report_models: Iterable[Dict[str, Any]],
    columns: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    column_lookup = _column_lookup(columns)
    reports = []
    field_occurrences: Dict[str, Dict[str, Any]] = {}

    for item in report_models:
        report = dict(item.get("report") or {})
        model = item.get("model") or {}
        report_id = str(report.get("internalName") or report.get("id") or report.get("displayName") or "").strip()
        if not report_id:
            continue
        reports.append(
            {
                "id": report_id,
                "displayName": report.get("displayName") or report_id,
                "internalName": report.get("internalName") or report_id,
                "source": item.get("source") or "report",
            }
        )
        for group in ((model.get("checks") or {}).get("groups") or []):
            field_name = _group_internal_name(group, column_lookup)
            if not field_name:
                continue
            column = column_lookup.get(_key(field_name), {})
            display_name = str(column.get("displayName") or group.get("displayName") or field_name).strip()
            canonical_key = _key(display_name or field_name)
            if not canonical_key:
                continue
            designation = _designation(group)
            description = str(group.get("description") or column.get("description") or "").strip()
            rules = list(group.get("rules") or [])
            normalized_rules = _normalized_rules(rules, field_name)
            fingerprint = _fingerprint_normalized_rules(normalized_rules)
            field_entry = field_occurrences.setdefault(
                canonical_key,
                {
                    "key": canonical_key,
                    "displayName": display_name,
                    "designation": designation,
                    "description": description,
                    "occurrences": [],
                },
            )
            if not field_entry["designation"] and designation:
                field_entry["designation"] = designation
            if not field_entry["description"] and description:
                field_entry["description"] = description
            field_entry["occurrences"].append(
                {
                    "reportId": report_id,
                    "internalName": field_name,
                    "ruleCount": len(rules),
                    "activeRuleCount": sum(1 for rule in rules if bool(rule.get("active"))),
                    "fingerprint": fingerprint,
                    "_normalizedRules": normalized_rules,
                    "dimensions": sorted({str(rule.get("dimension") or "Ohne Typ") for rule in rules}),
                }
            )

    reports.sort(key=lambda item: str(item["displayName"]).casefold())
    fields = []
    divergent_count = 0
    missing_count = 0
    for field in field_occurrences.values():
        fingerprints = Counter(item["fingerprint"] for item in field["occurrences"])
        reference_fingerprint = max(fingerprints, key=lambda fingerprint: fingerprints[fingerprint])
        reference_occurrence = next(
            item for item in field["occurrences"] if item["fingerprint"] == reference_fingerprint
        )
        report_entries = {}
        for occurrence in field["occurrences"]:
            status = "aligned" if occurrence["fingerprint"] == reference_fingerprint else "divergent"
            differences = _rule_differences(
                reference_occurrence["_normalizedRules"],
                occurrence["_normalizedRules"],
                reference_occurrence["internalName"],
                occurrence["internalName"],
            )
            report_entries[occurrence["reportId"]] = {
                **{key: value for key, value in occurrence.items() if key != "_normalizedRules"},
                "status": status,
                "differences": differences,
            }
            if status == "divergent":
                divergent_count += 1
        missing_for_field = len(reports) - len(report_entries)
        missing_count += missing_for_field
        fields.append(
            {
                **{key: value for key, value in field.items() if key != "occurrences"},
                "referenceFingerprint": reference_fingerprint,
                "referenceReportId": reference_occurrence["reportId"],
                "reportCount": len(report_entries),
                "missingReportCount": missing_for_field,
                "reports": report_entries,
            }
        )
    fields.sort(key=lambda item: str(item["displayName"]).casefold())
    return {
        "reports": reports,
        "fields": fields,
        "summary": {
            "reportCount": len(reports),
            "fieldCount": len(fields),
            "divergentCount": divergent_count,
            "missingCount": missing_count,
        },
    }


def prepare_group_transfer(
    report_models: Iterable[Dict[str, Any]],
    columns: Iterable[Dict[str, Any]],
    field_key: str,
    source_report_id: str,
    target_report_ids: Iterable[str],
) -> Dict[str, Any]:
    items = list(report_models)
    column_lookup = _column_lookup(columns)
    by_report = {_report_id(item): item for item in items if _report_id(item)}
    source_item = by_report.get(str(source_report_id))
    if not source_item:
        raise HarmonizationError("Der ausgewählte Referenzbericht wurde nicht gefunden.")

    source_group = _find_group(source_item.get("model") or {}, field_key, column_lookup)
    if not source_group:
        raise HarmonizationError("Die Referenz-Regelgruppe wurde im ausgewählten Bericht nicht gefunden.")
    source_internal = _group_internal_name(source_group, column_lookup)
    if not source_internal:
        raise HarmonizationError("Die Referenz-Regelgruppe besitzt keinen Internalname.")

    unique_targets = []
    for report_id in target_report_ids:
        normalized_id = str(report_id).strip()
        if normalized_id and normalized_id != source_report_id and normalized_id not in unique_targets:
            unique_targets.append(normalized_id)
    if not unique_targets:
        raise HarmonizationError("Es wurde kein Zielbericht ausgewählt.")

    changes = []
    for target_report_id in unique_targets:
        target_item = by_report.get(target_report_id)
        if not target_item:
            raise HarmonizationError(f"Zielbericht nicht gefunden: {target_report_id}")
        old_model = deepcopy(target_item.get("model") or {})
        new_model = deepcopy(old_model)
        groups = (new_model.setdefault("checks", {})).setdefault("groups", [])
        old_group_index = _find_group_index(new_model, field_key, column_lookup)
        old_group = deepcopy(groups[old_group_index]) if old_group_index is not None else None
        target_internal = _group_internal_name(old_group or {}, column_lookup) or source_internal
        transferred_group = _transfer_group(source_group, source_internal, target_internal)
        if old_group_index is None:
            groups.append(transferred_group)
            action = "create"
            group_index = len(groups) - 1
            _ensure_source_attribute(new_model, transferred_group)
        else:
            groups[old_group_index] = transferred_group
            action = "replace"
            group_index = old_group_index
        _renumber_groups(groups)
        normalized_model = normalize_editor_model(new_model)
        target_report = dict(target_item.get("report") or {})
        changes.append(
            {
                "reportId": target_report_id,
                "reportName": target_report.get("displayName") or target_report_id,
                "action": action,
                "groupIndex": group_index,
                "internalName": target_internal,
                "oldRuleCount": len((old_group or {}).get("rules") or []),
                "newRuleCount": len(transferred_group.get("rules") or []),
                "oldModel": old_model,
                "editorModel": normalized_model,
            }
        )

    source_report = dict(source_item.get("report") or {})
    return {
        "fieldKey": field_key,
        "source": {
            "reportId": source_report_id,
            "reportName": source_report.get("displayName") or source_report_id,
            "internalName": source_internal,
            "ruleCount": len(source_group.get("rules") or []),
        },
        "changes": changes,
        "summary": {
            "targetCount": len(changes),
            "createCount": sum(1 for change in changes if change["action"] == "create"),
            "replaceCount": sum(1 for change in changes if change["action"] == "replace"),
        },
    }


def _column_lookup(columns: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for column in columns:
        for value in (column.get("internalName"), column.get("importName"), column.get("displayName")):
            key = _key(value)
            if key:
                lookup.setdefault(key, column)
    return lookup


def _report_id(item: Dict[str, Any]) -> str:
    report = item.get("report") or {}
    return str(report.get("internalName") or report.get("id") or report.get("displayName") or "").strip()


def _find_group(model: Dict[str, Any], field_key: str, column_lookup: Dict[str, Dict[str, Any]]):
    index = _find_group_index(model, field_key, column_lookup)
    groups = ((model.get("checks") or {}).get("groups") or [])
    return groups[index] if index is not None else None


def _find_group_index(
    model: Dict[str, Any],
    field_key: str,
    column_lookup: Dict[str, Dict[str, Any]],
):
    for index, group in enumerate(((model.get("checks") or {}).get("groups") or [])):
        internal_name = _group_internal_name(group, column_lookup)
        column = column_lookup.get(_key(internal_name), {})
        canonical_key = _key(column.get("displayName") or group.get("displayName") or internal_name)
        if canonical_key == field_key:
            return index
    return None


def _group_internal_name(
    group: Dict[str, Any],
    column_lookup: Dict[str, Dict[str, Any]] | None = None,
) -> str:
    explicit = str(group.get("internalName") or group.get("field") or "").strip()
    if explicit:
        return explicit

    candidates = []
    for rule in group.get("rules") or []:
        expression = str(rule.get("expression") or "").strip()
        if expression:
            candidates.append(expression)
        candidates.extend(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", str(rule.get("condition") or "")))
    title_field = str(group.get("title") or "").split("(", 1)[0].strip()
    if title_field:
        candidates.append(title_field)

    if column_lookup:
        for candidate in candidates:
            column = column_lookup.get(_key(candidate))
            if column:
                return str(column.get("internalName") or candidate).strip()
    return candidates[0] if candidates else ""


def _transfer_group(group: Dict[str, Any], source_internal: str, target_internal: str) -> Dict[str, Any]:
    transferred = deepcopy(group)
    transferred["internalName"] = target_internal
    transferred["field"] = target_internal
    for key in ("title", "expression"):
        if key in transferred:
            transferred[key] = _replace_identifier(str(transferred.get(key) or ""), source_internal, target_internal)
    for rule in transferred.get("rules") or []:
        for key in ("condition", "expression"):
            if key in rule:
                rule[key] = _replace_identifier(str(rule.get(key) or ""), source_internal, target_internal)
    return transferred


def _replace_identifier(value: str, source: str, target: str) -> str:
    if not source or source.casefold() == target.casefold():
        return value
    return re.sub(
        rf"(?<![A-Za-z0-9_]){re.escape(source)}(?![A-Za-z0-9_])",
        lambda _: target,
        value,
        flags=re.IGNORECASE,
    )


def _ensure_source_attribute(model: Dict[str, Any], group: Dict[str, Any]) -> None:
    source = model.setdefault("source", {})
    attributes = source.setdefault("attributes", [])
    internal_name = _group_internal_name(group)
    if any(_key(attribute.get("name")) == _key(internal_name) for attribute in attributes):
        return
    attributes.append(
        {
            "name": internal_name,
            "expression": internal_name,
            "comment": str(group.get("description") or "").strip(),
        }
    )


def _renumber_groups(groups: list[Dict[str, Any]]) -> None:
    for index, group in enumerate(groups, start=1):
        group["number"] = index


def _rule_fingerprint(rules: Iterable[Dict[str, Any]], field_name: str) -> str:
    return _fingerprint_normalized_rules(_normalized_rules(rules, field_name))


def _normalized_rules(rules: Iterable[Dict[str, Any]], field_name: str) -> list[Dict[str, Any]]:
    normalized = []
    field_pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(field_name)}(?![A-Za-z0-9_])", re.IGNORECASE)
    for rule in rules:
        condition = field_pattern.sub("{{field}}", str(rule.get("condition") or ""))
        normalized.append(
            {
                "condition": _space(condition),
                "message": _space(str(rule.get("message") or "")),
                "dimension": _space(str(rule.get("dimension") or "")),
                "ruleType": _space(str(rule.get("ruleType") or "custom")),
                "active": bool(rule.get("active")),
            }
        )
    return normalized


def _fingerprint_normalized_rules(rules: Iterable[Dict[str, Any]]) -> str:
    canonical = [
        {
            key: value.casefold() if isinstance(value, str) else value
            for key, value in rule.items()
        }
        for rule in rules
    ]
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _rule_differences(
    reference_rules: list[Dict[str, Any]],
    current_rules: list[Dict[str, Any]],
    reference_field: str,
    current_field: str,
) -> list[Dict[str, Any]]:
    differences = []
    count = max(len(reference_rules), len(current_rules))
    for index in range(count):
        reference = reference_rules[index] if index < len(reference_rules) else None
        current = current_rules[index] if index < len(current_rules) else None
        if reference is None or current is None:
            differences.append(
                {
                    "ruleNumber": index + 1,
                    "property": "rule",
                    "referenceValue": "Fehlt" if reference is None else "Vorhanden",
                    "currentValue": "Fehlt" if current is None else "Vorhanden",
                }
            )
            continue
        for property_name in ("condition", "message", "dimension", "ruleType", "active"):
            reference_value = reference[property_name]
            current_value = current[property_name]
            canonical_reference = reference_value.casefold() if isinstance(reference_value, str) else reference_value
            canonical_current = current_value.casefold() if isinstance(current_value, str) else current_value
            if canonical_reference == canonical_current:
                continue
            differences.append(
                {
                    "ruleNumber": index + 1,
                    "property": property_name,
                    "referenceValue": _display_difference_value(reference_value, reference_field),
                    "currentValue": _display_difference_value(current_value, current_field),
                }
            )
    return differences


def _display_difference_value(value: Any, field_name: str) -> Any:
    if isinstance(value, str):
        return value.replace("{{field}}", field_name)
    return value


def _designation(group: Dict[str, Any]) -> str:
    for value in (group.get("displayName"), group.get("title")):
        match = re.search(r"\(([^()]+)\)\s*$", str(value or ""))
        if match:
            return match.group(1).strip()
    return ""


def _space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())
