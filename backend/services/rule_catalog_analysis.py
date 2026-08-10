import hashlib
import re
from collections import Counter
from typing import Any, Dict, Iterable


RULE_TYPE_NAMES = {
    "completeness": "Pflichtfeldprüfung",
    "trim_whitespace": "Leerzeichenprüfung",
    "min_length": "Mindestlänge",
    "max_length": "Maximallänge",
    "regex": "Musterprüfung",
    "obsolete_terms": "Obsolete Begriffe",
    "mixed_umlaut_spelling": "Schreibweisenprüfung",
    "custom": "Individuelle Datenqualitätsregel",
}


def analyze_rule_catalog_candidates(
    report_models: Iterable[Dict[str, Any]],
    existing_templates: Iterable[Any],
) -> Dict[str, Any]:
    existing_signatures = {
        _signature(
            template.version.conditionTemplate,
            template.version.dimension,
            template.version.ruleType,
        ): template
        for template in existing_templates
    }
    clusters: Dict[str, Dict[str, Any]] = {}
    scanned_reports = 0
    scanned_rules = 0

    for item in report_models:
        report = item.get("report") or {}
        model = item.get("model") or {}
        report_ref = str(report.get("internalName") or report.get("id") or report.get("displayName") or "").strip()
        if not report_ref:
            continue
        scanned_reports += 1
        for group_index, group in enumerate(((model.get("checks") or {}).get("groups") or [])):
            internal_name = str(group.get("internalName") or group.get("field") or "").strip()
            if not internal_name:
                continue
            display_name = str(group.get("displayName") or internal_name).strip()
            designation = _designation(group)
            group_ref = str(group.get("id") or internal_name or f"group_{group_index + 1}")
            for rule_index, rule in enumerate(group.get("rules") or []):
                condition = str(rule.get("condition") or "").strip()
                if not condition:
                    continue
                scanned_rules += 1
                dimension = str(rule.get("dimension") or "Ohne Typ").strip()
                rule_type = str(rule.get("ruleType") or "custom").strip()
                generic_condition = _replace_identifier(condition, internal_name, "{field}")
                parameterized = _parameterize_condition(generic_condition, rule_type)
                generic_message = _generalize_message(
                    str(rule.get("message") or "").strip(),
                    internal_name,
                    display_name,
                    designation,
                )
                generic_message = _parameterize_message(generic_message, parameterized["parameters"])
                signature = _signature(parameterized["condition"], dimension, rule_type)
                candidate_key = _candidate_key(rule_type, signature)
                cluster = clusters.setdefault(
                    signature,
                    {
                        "key": candidate_key,
                        "conditionTemplate": parameterized["condition"],
                        "dimension": dimension,
                        "ruleType": rule_type,
                        "parameterSchema": parameterized["schema"],
                        "parameterValues": {},
                        "messages": Counter(),
                        "locations": [],
                        "fields": set(),
                        "reports": set(),
                        "activeCount": 0,
                    },
                )
                cluster["messages"][generic_message] += 1
                cluster["fields"].add(internal_name)
                cluster["reports"].add(report_ref)
                cluster["activeCount"] += int(bool(rule.get("active")))
                for name, value in parameterized["parameters"].items():
                    cluster["parameterValues"].setdefault(name, Counter())[value] += 1
                cluster["locations"].append(
                    {
                        "reportRef": report_ref,
                        "reportName": report.get("displayName") or report_ref,
                        "groupRef": group_ref,
                        "groupName": display_name,
                        "field": internal_name,
                        "ruleRef": str(rule.get("id") or f"{group_ref}_rule_{rule_index + 1}"),
                        "active": bool(rule.get("active")),
                        "parameters": parameterized["parameters"],
                    }
                )

    candidates = []
    for signature, cluster in clusters.items():
        existing = existing_signatures.get(signature)
        message_variants = [
            {"message": message, "count": count}
            for message, count in cluster["messages"].most_common()
            if message
        ]
        preferred_message = message_variants[0]["message"] if message_variants else "{displayName} ist fehlerhaft"
        message_de, message_en = _language_messages(message_variants)
        occurrence_count = len(cluster["locations"])
        candidates.append(
            {
                "key": cluster["key"],
                "name": RULE_TYPE_NAMES.get(cluster["ruleType"], cluster["ruleType"] or "Datenqualitätsregel"),
                "description": (
                    f"Automatisch aus {occurrence_count} bestehenden Regelvorkommen "
                    f"in {len(cluster['reports'])} Berichten erkannt."
                ),
                "conditionTemplate": cluster["conditionTemplate"],
                "messageDeTemplate": message_de or preferred_message,
                "messageEnTemplate": message_en,
                "dimension": cluster["dimension"],
                "ruleType": cluster["ruleType"],
                "parameterSchema": cluster["parameterSchema"],
                "parameterVariants": {
                    name: [
                        {"value": value, "count": count}
                        for value, count in values.most_common()
                    ]
                    for name, values in cluster["parameterValues"].items()
                },
                "compatibleDataTypes": [],
                "fieldCategories": ["master-data"],
                "occurrenceCount": occurrence_count,
                "reportCount": len(cluster["reports"]),
                "fieldCount": len(cluster["fields"]),
                "activeCount": cluster["activeCount"],
                "messageVariants": message_variants,
                "locations": cluster["locations"],
                "existingTemplateId": existing.id if existing else None,
                "existingTemplateName": existing.name if existing else None,
                "confidence": _confidence(occurrence_count, len(message_variants), cluster["ruleType"]),
            }
        )
    candidates.sort(
        key=lambda candidate: (
            bool(candidate["existingTemplateId"]),
            -candidate["occurrenceCount"],
            candidate["name"].casefold(),
            candidate["key"],
        )
    )
    return {
        "summary": {
            "reportCount": scanned_reports,
            "ruleCount": scanned_rules,
            "candidateCount": len(candidates),
            "newCandidateCount": sum(1 for candidate in candidates if not candidate["existingTemplateId"]),
            "cataloguedCount": sum(1 for candidate in candidates if candidate["existingTemplateId"]),
        },
        "candidates": candidates,
    }


def _signature(condition: str, dimension: str, rule_type: str) -> str:
    return "\0".join(
        (
            _space(condition).casefold(),
            _space(dimension).casefold(),
            _space(rule_type or "custom").casefold(),
        )
    )


def _candidate_key(rule_type: str, signature: str) -> str:
    prefix = re.sub(r"[^a-z0-9]+", "_", str(rule_type or "custom").casefold()).strip("_") or "custom"
    digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:10]
    return f"imported_{prefix}_{digest}"


def _replace_identifier(value: str, identifier: str, replacement: str) -> str:
    return re.sub(
        rf"(?<![A-Za-z0-9_]){re.escape(identifier)}(?![A-Za-z0-9_])",
        lambda _: replacement,
        value,
        flags=re.IGNORECASE,
    )


def _generalize_message(message: str, internal_name: str, display_name: str, designation: str) -> str:
    result = message
    candidates = sorted(
        {value for value in (display_name, designation, internal_name) if value},
        key=len,
        reverse=True,
    )
    for value in candidates:
        result = re.sub(re.escape(value), "{displayName}", result, flags=re.IGNORECASE)
    return _space(result)


def _parameterize_condition(condition: str, rule_type: str) -> Dict[str, Any]:
    normalized_type = str(rule_type or "").strip().casefold()
    if normalized_type in {"min_length", "max_length"}:
        parameter_name = normalized_type
        pattern = re.compile(
            r"(?P<prefix>\bLENGTH\s*\(\s*(?:TRIM\s*\(\s*)?\{field\}\s*\)?\s*\)"
            r"\s*(?:<=|>=|<>|=|<|>)\s*)"
            r"(?P<value>-?\d+(?:\.\d+)?)",
            flags=re.IGNORECASE,
        )
        match = pattern.search(condition)
        if match:
            value = _numeric_value(match.group("value"))
            parameter_type = "integer" if isinstance(value, int) else "number"
            parameterized = condition[: match.start("value")] + f"{{{parameter_name}}}" + condition[match.end("value") :]
            return {
                "condition": parameterized,
                "schema": {
                    parameter_name: {
                        "type": parameter_type,
                        "required": True,
                        "min": 0,
                    }
                },
                "parameters": {parameter_name: value},
            }

    if normalized_type == "regex":
        matches = list(
            re.finditer(
                r"(?P<prefix>\b(?:NOT\s+)?LIKE_REGEXPR\s*)"
                r"(?P<literal>'(?:''|[^'])*')",
                condition,
                flags=re.IGNORECASE,
            )
        )
        if matches:
            parameters: Dict[str, Any] = {}
            schema: Dict[str, Any] = {}
            parts = []
            cursor = 0
            for index, match in enumerate(matches, start=1):
                name = "pattern" if len(matches) == 1 else f"pattern_{index}"
                parts.append(condition[cursor : match.start("literal")])
                parts.append(f"{{{name}}}")
                cursor = match.end("literal")
                parameters[name] = _sql_string_value(match.group("literal"))
                schema[name] = {"type": "regex", "required": True}
            parts.append(condition[cursor:])
            return {
                "condition": "".join(parts),
                "schema": schema,
                "parameters": parameters,
            }

    return {"condition": condition, "schema": {}, "parameters": {}}


def _parameterize_message(message: str, parameters: Dict[str, Any]) -> str:
    result = message
    for name, value in parameters.items():
        text = str(value)
        if not text:
            continue
        if isinstance(value, (int, float)):
            result = re.sub(
                rf"(?<![A-Za-z0-9_.]){re.escape(text)}(?![A-Za-z0-9_.])",
                f"{{{name}}}",
                result,
            )
        elif len(text) >= 4:
            result = result.replace(text, f"{{{name}}}")
    return result


def _numeric_value(value: str) -> int | float:
    return float(value) if "." in value else int(value)


def _sql_string_value(literal: str) -> str:
    return literal[1:-1].replace("''", "'")


def _designation(group: Dict[str, Any]) -> str:
    for value in (group.get("displayName"), group.get("title")):
        match = re.search(r"\(([^()]+)\)\s*$", str(value or ""))
        if match:
            return match.group(1).strip()
    return ""


def _language_messages(variants: list[Dict[str, Any]]) -> tuple[str, str]:
    german = ""
    english = ""
    for variant in variants:
        message = variant["message"]
        if _looks_english(message):
            english = english or message
        else:
            german = german or message
    return german, english


def _looks_english(value: str) -> bool:
    words = set(re.findall(r"[a-z]+", str(value).casefold()))
    return bool(words & {"is", "invalid", "missing", "empty", "contains", "too", "short", "long", "obsolete"})


def _confidence(occurrences: int, variants: int, rule_type: str) -> float:
    score = 0.62
    if occurrences >= 2:
        score += 0.12
    if occurrences >= 5:
        score += 0.1
    if variants <= 1:
        score += 0.08
    if rule_type and rule_type != "custom":
        score += 0.05
    return round(min(score, 0.97), 2)


def _space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()
