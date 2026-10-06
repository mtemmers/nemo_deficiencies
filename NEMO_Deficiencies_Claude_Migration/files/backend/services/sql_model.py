import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

DQ_DIMENSIONS = {
    "vollständigkeit": "Vollständigkeit",
    "vollstaendigkeit": "Vollständigkeit",
    "validität": "Validität",
    "validitaet": "Validität",
    "korrektheit": "Korrektheit",
    "eindeutigkeit": "Eindeutigkeit",
    "konsistenz": "Konsistenz",
    "aktualität": "Aktualität",
    "aktualitaet": "Aktualität",
    "genauigkeit": "Genauigkeit",
    "redundanz": "Redundanz",
    "einheitlichkeit": "Einheitlichkeit",
    "relevanz": "Relevanz",
    "zuverlässigkeit": "Zuverlässigkeit",
    "zuverlaessigkeit": "Zuverlässigkeit",
    "verständlichkeit": "Verständlichkeit",
    "verstaendlichkeit": "Verständlichkeit",
}

SQL_KEYWORDS = {
    "AND",
    "AS",
    "CASE",
    "CAST",
    "COALESCE",
    "CURRENT_DATE",
    "ELSE",
    "END",
    "FLAG",
    "IS",
    "LENGTH",
    "LIKE_REGEXPR",
    "NOT",
    "NULL",
    "OR",
    "REPLACE_REGEXPR",
    "SELECT",
    "THEN",
    "TRIM",
    "WHEN",
    "WITH",
}


@dataclass(frozen=True)
class ValidationFinding:
    severity: str
    code: str
    message: str
    groupId: Optional[str] = None
    ruleId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_editor_model(sql: str, report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    report = report or {}
    blocks = parse_blocks(sql)
    groups = parse_check_groups(sql)
    output_fields = parse_output_fields(sql)
    source_attributes = parse_source_attributes(sql, blocks)
    source_settings = parse_source_settings(sql, blocks)
    stats = build_stats(groups, blocks, output_fields, source_attributes)
    validation = validate_parts(sql, blocks, groups)

    return {
        "version": 1,
        "report": {
            "id": report.get("id") or "",
            "displayName": report.get("displayName") or "",
            "internalName": report.get("internalName") or "",
        },
        "summary": stats,
        "blocks": blocks,
        "source": {"attributes": source_attributes, **source_settings},
        "checks": {"groups": groups},
        "output": {"fields": output_fields},
        "validation": validation,
    }


def parse_blocks(sql: str) -> List[Dict[str, Any]]:
    if not sql.strip():
        return []

    cte_matches = list(re.finditer(r"(?im)^\s*(?:WITH\s+)?([A-Za-z_][\w]*)\s+AS\s*\(", sql))
    final_select_start = find_final_select_start(sql)
    blocks: List[Dict[str, Any]] = []

    for index, match in enumerate(cte_matches):
        name = match.group(1)
        next_start = cte_matches[index + 1].start() if index + 1 < len(cte_matches) else final_select_start or len(sql)
        segment = sql[match.start():next_start]
        block_type = classify_block(name, index)
        blocks.append(
            {
                "id": block_type,
                "cteName": name,
                "title": block_title(block_type, name),
                "lineStart": line_number(sql, match.start()),
                "lineEnd": line_number(sql, max(match.start(), next_start - 1)),
                "characters": len(segment),
            }
        )

    if final_select_start is not None:
        blocks.append(
            {
                "id": "output",
                "cteName": "",
                "title": "Standardisierte Ausgabe",
                "lineStart": line_number(sql, final_select_start),
                "lineEnd": line_number(sql, len(sql)),
                "characters": len(sql) - final_select_start,
            }
        )

    return blocks


def parse_check_groups(sql: str) -> List[Dict[str, Any]]:
    segment = checks_segment(sql)
    if not segment:
        return []

    groups: List[Dict[str, Any]] = []
    previous_end = 0
    for case_index, match in enumerate(re.finditer(r"(?is)\bCASE\b(?P<body>.*?)\bELSE\s+''\s*END", segment), start=1):
        header = segment[previous_end:match.start()]
        body = match.group("body")
        meta = parse_group_header(header, case_index)
        rules = parse_rules(body, group_id=f"group_{case_index:03d}")
        groups.append(
            {
                "id": f"group_{case_index:03d}",
                "number": case_index,
                "title": meta["title"],
                "displayName": meta["displayName"],
                "internalName": meta["internalName"],
                "field": meta["field"],
                "description": meta["description"],
                "typeHints": meta["typeHints"],
                "lineStart": line_number(sql, sql.find(match.group(0))),
                "rules": rules,
                "activeRules": sum(1 for rule in rules if rule["active"]),
                "inactiveRules": sum(1 for rule in rules if not rule["active"]),
            }
        )
        previous_end = match.end()

    return groups


def parse_rules(case_body: str, group_id: str) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []
    previous_end = 0
    pattern = re.compile(r"(?ims)^\s*WHEN\s+(?P<condition>.*?)(?:^\s*THEN\s+(?P<then>[^\n]*))")

    for index, match in enumerate(pattern.finditer(case_body), start=1):
        prefix = case_body[previous_end:match.start()]
        comments = comment_lines(prefix)
        condition = clean_condition(match.group("condition"))
        then_value = (match.group("then") or "").strip()
        message, active = parse_then_message(then_value)
        rule_type = infer_rule_type(condition, message)
        dimension = last_dimension(comments) or infer_rule_dimension(condition, message, rule_type)
        rule_id = f"{group_id}_rule_{index:03d}"
        rules.append(
            {
                "id": rule_id,
                "number": index,
                "dimension": dimension,
                "ruleType": rule_type,
                "expression": infer_expression(condition),
                "condition": condition,
                "message": message,
                "active": active,
                "comment": comments[-1] if comments else "",
            }
        )
        previous_end = match.end()

    return rules


def parse_group_header(header: str, fallback_number: int) -> Dict[str, Any]:
    comments = comment_lines(header)
    title = f"Prüfung {fallback_number}"
    field = ""
    description = ""
    display_name = ""
    type_hints: List[str] = []

    for comment in comments:
        title_match = re.search(r"PR[ÜU]FUNG\s+\d+\s*:\s*(.+)", comment, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            display_match = re.match(r"^.+?\s*\((.+)\)$", title)
            if display_match:
                display_name = display_match.group(1).strip()

        check_group_match = re.match(r"CHECK\s+GROUP\s+\d+\s*:\s*(.*?)\s*\(([^)]+)\)\s*$", comment, re.IGNORECASE)
        if check_group_match:
            title = check_group_match.group(1).strip()
            field = check_group_match.group(2).strip()
            continue

        field_match = re.match(r"([A-Z][A-Z0-9_\-]+(?:-[0-9]+)?)\s*(?:\((.*?)\))?$", comment)
        if field_match and "TYPEN:" not in comment.upper() and not comment.upper().startswith("PRÜFUNG"):
            field = field_match.group(1).strip()

        if "Typen:" in comment:
            before_types, after_types = comment.split("Typen:", 1)
            description = before_types.strip(" |") or description
            type_hints = [item.strip() for item in after_types.split(",") if item.strip()]
        elif comment and not comment.startswith("=") and not re.match(r"(?:PR[ÜU]FUNG|CHECK\s+GROUP)\s+\d+", comment, re.IGNORECASE):
            if not description and not field_match:
                description = comment

    return {
        "title": title,
        "displayName": display_name or title,
        "internalName": field,
        "field": field,
        "description": description,
        "typeHints": type_hints,
    }


def parse_source_attributes(sql: str, blocks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    source_block = next((block for block in blocks if block["id"] == "source"), None)
    if not source_block:
        return []

    lines = sql.splitlines()
    start = max(source_block["lineStart"] - 1, 0)
    end = min(source_block["lineEnd"], len(lines))
    segment = "\n".join(lines[start:end])
    select_match = re.search(r"(?is)\bSELECT\b(?P<select>.*?)\bFROM\b", segment)
    if not select_match:
        return []

    attributes: List[Dict[str, str]] = []
    for raw_line in select_match.group("select").splitlines():
        comment = ""
        if "--" in raw_line:
            raw_line, comment = raw_line.split("--", 1)
            comment = comment.strip()
        expression = raw_line.strip().strip(",")
        if not expression:
            continue
        alias = alias_from_expression(expression)
        if alias:
            attributes.append({"name": alias, "expression": expression, "comment": comment})
    return attributes


def parse_source_settings(sql: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    source_block = next((block for block in blocks if block["id"] == "source"), None)
    if not source_block:
        return {"masterDataSubType": "", "exceptions": []}

    lines = sql.splitlines()
    start = max(source_block["lineStart"] - 1, 0)
    end = min(source_block["lineEnd"], len(lines))
    segment = "\n".join(lines[start:end])
    subtype_match = re.search(
        r"(?is)UPPER\s*\(\s*TRIM\s*\(\s*MASTER_DATA_SUB_TYPE\s*\)\s*\)\s*=\s*'((?:''|[^'])*)'",
        segment,
    )
    master_data_sub_type = subtype_match.group(1).replace("''", "'") if subtype_match else ""

    exceptions: List[Dict[str, Any]] = []
    for match in re.finditer(r"(?is)\bAND\s+([A-Za-z_][\w]*)\s+NOT\s+IN\s*\((.*?)\)", segment):
        values = [value.replace("''", "'") for value in re.findall(r"'((?:''|[^'])*)'", match.group(2))]
        exceptions.append({"field": match.group(1), "operator": "NOT IN", "values": values})
    return {"masterDataSubType": master_data_sub_type, "exceptions": exceptions}


def parse_output_fields(sql: str) -> List[Dict[str, str]]:
    start = find_final_select_start(sql)
    if start is None:
        return []

    segment = sql[start:]
    select_match = re.search(r"(?is)\bSELECT\b(?P<select>.*?)\bFROM\b", segment)
    if not select_match:
        return []

    fields: List[Dict[str, str]] = []
    for raw_line in select_match.group("select").splitlines():
        expression = raw_line.split("--", 1)[0].strip().strip(",")
        if not expression:
            continue
        alias = alias_from_expression(expression)
        if alias:
            fields.append({"name": alias, "expression": expression})
    return fields


def validate_parts(sql: str, blocks: List[Dict[str, Any]], groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    findings: List[ValidationFinding] = []

    if not sql.strip():
        findings.append(ValidationFinding("error", "empty_sql", "Kein SQL vorhanden."))
    if not any(block["id"] == "checks" for block in blocks):
        findings.append(ValidationFinding("warning", "missing_checks_block", "Kein checks-Block erkannt."))
    if "WHEN WHEN" in sql.upper():
        findings.append(ValidationFinding("warning", "duplicated_when", "Mindestens eine Regel enthält 'WHEN WHEN'."))

    for group in groups:
        if not group["typeHints"]:
            findings.append(
                ValidationFinding("info", "missing_type_hints", "Gruppe enthält keine Typen-Zeile.", groupId=group["id"])
            )
        for rule in group["rules"]:
            if rule["active"] and not rule["dimension"]:
                findings.append(
                    ValidationFinding(
                        "warning",
                        "missing_dimension",
                        "Aktive Regel hat keine fachliche Dimension.",
                        groupId=group["id"],
                        ruleId=rule["id"],
                    )
                )
            if rule["message"] in {"", "|"}:
                findings.append(
                    ValidationFinding(
                        "info",
                        "placeholder_message",
                        "Regel hat keine fachliche Fehlermeldung.",
                        groupId=group["id"],
                        ruleId=rule["id"],
                    )
                )

    severities = Counter(finding.severity for finding in findings)
    return {
        "ok": not any(finding.severity == "error" for finding in findings),
        "counts": dict(severities),
        "findings": [finding.to_dict() for finding in findings],
    }


def build_stats(
    groups: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    output_fields: List[Dict[str, str]],
    source_attributes: List[Dict[str, str]],
) -> Dict[str, Any]:
    rules = [rule for group in groups for rule in group["rules"]]
    dimension_counts = Counter(rule["dimension"] or "Ohne Dimension" for rule in rules)
    return {
        "blockCount": len(blocks),
        "sourceAttributeCount": len(source_attributes),
        "outputFieldCount": len(output_fields),
        "checkGroupCount": len(groups),
        "ruleCount": len(rules),
        "activeRuleCount": sum(1 for rule in rules if rule["active"]),
        "inactiveRuleCount": sum(1 for rule in rules if not rule["active"]),
        "dimensionCounts": dict(dimension_counts),
    }


def checks_segment(sql: str) -> str:
    match = re.search(r"(?im)^\s*checks\s+AS\s*\(", sql)
    if not match:
        return ""
    final_select = find_final_select_start(sql)
    end = final_select if final_select is not None and final_select > match.start() else len(sql)
    return sql[match.start():end]


def find_final_select_start(sql: str) -> Optional[int]:
    matches = list(re.finditer(r"(?im)^\s*SELECT\s*$", sql))
    if not matches:
        matches = list(re.finditer(r"(?im)^\s*SELECT\b", sql))
    return matches[-1].start() if matches else None


def classify_block(name: str, index: int) -> str:
    lowered = name.casefold()
    if "check" in lowered:
        return "checks"
    if "join" in lowered:
        return "join"
    if "proc" in lowered or "process" in lowered:
        return "process"
    if index == 0 or "source" in lowered or lowered.endswith("src"):
        return "source"
    return "cte"


def block_title(block_type: str, name: str) -> str:
    titles = {
        "source": "Attribute und Master-Data-Quelle",
        "process": "Prozessrelevanz",
        "join": "Prozessrelevante Daten",
        "checks": "Datenqualitätschecks",
        "output": "Standardisierte Ausgabe",
    }
    return titles.get(block_type, name)


def comment_lines(text: str) -> List[str]:
    comments: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            comments.append(stripped[2:].strip())
    return comments


def normalize_dimension(value: str) -> str:
    key = value.strip().casefold()
    return DQ_DIMENSIONS.get(key, "")


def last_dimension(comments: Iterable[str]) -> str:
    found = ""
    for comment in comments:
        dimension = normalize_dimension(comment)
        if dimension:
            found = dimension
    return found


def clean_condition(condition: str) -> str:
    cleaned = re.sub(r"\s+", " ", condition).strip()
    if cleaned.upper().startswith("WHEN "):
        cleaned = cleaned[5:].strip()
    return cleaned


def parse_then_message(then_value: str) -> tuple[str, bool]:
    literal = first_sql_literal(then_value)
    comment_literal = ""
    if "--" in then_value:
        comment_literal = first_sql_literal(then_value.split("--", 1)[1])

    if literal == "" and comment_literal:
        return normalize_rule_message(comment_literal), False
    if literal == "":
        return "", False
    return normalize_rule_message(literal), True


def normalize_rule_message(value: str) -> str:
    return re.sub(r"^\|+\s*", "", str(value or "").strip())


def first_sql_literal(text: str) -> str:
    match = re.search(r"'((?:''|[^'])*)'", text)
    if not match:
        return ""
    return match.group(1).replace("''", "'")


def infer_rule_type(condition: str, message: str) -> str:
    upper = condition.upper()
    lower_message = message.casefold()
    if "IS NULL" in upper or "= ''" in upper or "= ''" in condition:
        return "completeness"
    if "TRIM" in upper and ("<>" in condition or "!=" in condition):
        return "trim_whitespace"
    if "LENGTH" in upper and ">" in condition:
        return "max_length"
    if "LENGTH" in upper and "<" in condition:
        return "min_length"
    if "NOT LIKE_REGEXPR" in upper and "[\\P{L}]" in upper:
        return "missing_letters"
    if "obso" in lower_message or "test" in condition.casefold() or "inactive" in condition.casefold() or "inaktiv" in lower_message:
        return "obsolete_terms"
    if "umlaut" in lower_message or "ß" in lower_message:
        return "mixed_umlaut_spelling"
    if "rechtsform" in lower_message:
        return "legal_form_normalization"
    if "LIKE_REGEXPR" in upper:
        return "regex"
    return "custom"


def infer_rule_dimension(condition: str, message: str, rule_type: str = "") -> str:
    text = f"{condition} {message}".casefold()
    upper = condition.upper()
    if "IS NULL" in upper or "= ''" in condition or "leer" in text or "fehl" in text or "pflicht" in text:
        return "Vollständigkeit"
    if "obso" in text or "obsolete" in text or "inaktiv" in text or "inactive" in text or "test" in text or "veraltet" in text:
        return "Aktualität"
    if rule_type in {"trim_whitespace", "mixed_umlaut_spelling", "legal_form_normalization"}:
        return "Einheitlichkeit"
    if "leerzeichen" in text or "separator" in text or "umlaut" in text or "ß" in text or "rechtsform" in text or "schreibweise" in text:
        return "Einheitlichkeit"
    if rule_type in {"regex", "min_length", "max_length", "missing_letters"}:
        return "Korrektheit"
    if "LIKE_REGEXPR" in upper or "LENGTH" in upper or "ungültig" in text or "ungueltig" in text or "format" in text or "zu kurz" in text or "zu lang" in text:
        return "Korrektheit"
    defaults = {
        "completeness": "Vollständigkeit",
        "obsolete_terms": "Aktualität",
        "custom": "Korrektheit",
    }
    return defaults.get(rule_type, "Korrektheit")


def infer_expression(condition: str) -> str:
    identifiers = re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", condition)
    for identifier in identifiers:
        if identifier not in SQL_KEYWORDS:
            return identifier
    return ""


def alias_from_expression(expression: str) -> str:
    alias_match = re.search(r"(?i)\bAS\s+([A-Z_][A-Z0-9_]*)\s*$", expression)
    if alias_match:
        return alias_match.group(1)

    compact = expression.strip().rstrip(",")
    if re.match(r"^[A-Za-z_][\w\.]*$", compact):
        return compact.split(".")[-1]
    return ""


def line_number(sql: str, index: int) -> int:
    return sql.count("\n", 0, max(index, 0)) + 1


DQ_DIMENSION_VALUES = [
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

RULE_CATALOG = [
    {
        "id": "completeness",
        "label": "Pflichtfeld / Leerprüfung",
        "defaultDimension": "Vollständigkeit",
        "description": "Prüft NULL, leere Werte oder fehlende Pflichtdaten.",
    },
    {
        "id": "trim_whitespace",
        "label": "Leerzeichen bereinigen",
        "defaultDimension": "Einheitlichkeit",
        "description": "Prüft führende, folgende oder uneinheitliche Leerzeichen.",
    },
    {
        "id": "min_length",
        "label": "Mindestlänge",
        "defaultDimension": "Korrektheit",
        "description": "Prüft, ob ein Wert zu kurz ist.",
    },
    {
        "id": "max_length",
        "label": "Maximallänge",
        "defaultDimension": "Korrektheit",
        "description": "Prüft, ob ein Wert zu lang ist.",
    },
    {
        "id": "regex",
        "label": "Regex-Regel",
        "defaultDimension": "Korrektheit",
        "description": "Prüft erlaubte oder verbotene Muster.",
    },
    {
        "id": "obsolete_terms",
        "label": "Obsolete Begriffe",
        "defaultDimension": "Aktualität",
        "description": "Prüft Test-, Inaktiv-, Alt- oder Archiv-Begriffe.",
    },
    {
        "id": "mixed_umlaut_spelling",
        "label": "Umlaut-Schreibweise",
        "defaultDimension": "Einheitlichkeit",
        "description": "Prüft gemischte Schreibweisen wie ä/ae oder ß/ss.",
    },
    {
        "id": "legal_form_normalization",
        "label": "Rechtsform-Normalisierung",
        "defaultDimension": "Einheitlichkeit",
        "description": "Prüft Schreibweisen von GmbH, AG, KG, OHG und ähnlichen Formen.",
    },
    {
        "id": "custom",
        "label": "Sonderregel",
        "defaultDimension": "Korrektheit",
        "description": "Fachliche Sonderregel, die noch nicht katalogisiert ist.",
    },
]


def get_rule_catalog() -> Dict[str, Any]:
    return {
        "dimensions": DQ_DIMENSION_VALUES,
        "ruleTypes": RULE_CATALOG,
    }


def normalize_editor_rules(model: Dict[str, Any]) -> Dict[str, Any]:
    checks = model.get("checks")
    if not isinstance(checks, dict):
        checks = {}
        model["checks"] = checks
    groups = checks.get("groups")
    if not isinstance(groups, list):
        groups = []
        checks["groups"] = groups
    for group_index, group in enumerate(groups, start=1):
        group["number"] = group_index
        group["id"] = group.get("id") or f"group_{group_index:03d}"
        group["field"] = str(group.get("field") or "").strip()
        group["displayName"] = str(group.get("displayName") or group.get("title") or group.get("field") or "").strip()
        group["internalName"] = str(group.get("internalName") or group.get("field") or "").strip()
        group["description"] = str(group.get("description") or "").strip()
        group["title"] = str(group.get("title") or group.get("field") or f"Prüfung {group_index}").strip()
        group["typeHints"] = list(group.get("typeHints") or [])
        group["rules"] = list(group.get("rules") or [])
        for rule_index, rule in enumerate(group["rules"], start=1):
            condition = clean_condition(str(rule.get("condition") or ""))
            message = normalize_rule_message(str(rule.get("message") or ""))
            rule_type = rule.get("ruleType") or infer_rule_type(condition, message)
            dimension = normalize_dimension(rule.get("dimension") or "") or infer_rule_dimension(condition, message, rule_type)
            rule["id"] = rule.get("id") or f"{group['id']}_rule_{rule_index:03d}"
            rule["number"] = rule_index
            rule["condition"] = condition
            rule["message"] = message
            rule["ruleType"] = rule_type
            rule["dimension"] = dimension
            rule["active"] = bool(rule.get("active"))
    return model


def merge_missing_group_metadata(model: Dict[str, Any], original_model: Dict[str, Any]) -> Dict[str, Any]:
    groups = ((model.get("checks") or {}).get("groups") or [])
    original_groups = ((original_model.get("checks") or {}).get("groups") or [])
    for index, group in enumerate(groups):
        if index >= len(original_groups):
            break
        original = original_groups[index]
        for key in ("title", "displayName", "internalName", "field"):
            current = str(group.get(key) or "").strip()
            generic_title = key in {"title", "displayName"} and re.fullmatch(r"Prüfung\s+\d+", current, re.IGNORECASE)
            if not current or generic_title:
                group[key] = original.get(key) or current
    return model


def summarize_editor_model(model: Dict[str, Any]) -> Dict[str, Any]:
    groups = ((model.get("checks") or {}).get("groups") or [])
    blocks = model.get("blocks") or []
    source_attributes = ((model.get("source") or {}).get("attributes") or [])
    output_fields = ((model.get("output") or {}).get("fields") or [])
    rules = [rule for group in groups for rule in group.get("rules", [])]

    for group in groups:
        group_rules = group.get("rules", [])
        group["activeRules"] = sum(1 for rule in group_rules if bool(rule.get("active")))
        group["inactiveRules"] = sum(1 for rule in group_rules if not bool(rule.get("active")))

    dimension_counts = Counter((rule.get("dimension") or "Ohne Dimension") for rule in rules)
    summary = {
        "blockCount": len(blocks),
        "sourceAttributeCount": len(source_attributes),
        "outputFieldCount": len(output_fields),
        "checkGroupCount": len(groups),
        "ruleCount": len(rules),
        "activeRuleCount": sum(1 for rule in rules if bool(rule.get("active"))),
        "inactiveRuleCount": sum(1 for rule in rules if not bool(rule.get("active"))),
        "dimensionCounts": dict(dimension_counts),
    }
    model["summary"] = summary
    return summary


def validate_editor_model(model: Dict[str, Any]) -> Dict[str, Any]:
    findings: List[ValidationFinding] = []
    groups = ((model.get("checks") or {}).get("groups") or [])
    known_dimensions = set(DQ_DIMENSION_VALUES)
    known_rule_types = {item["id"] for item in RULE_CATALOG}

    if not groups:
        findings.append(ValidationFinding("error", "missing_groups", "Keine Regelgruppen im Editor-Modell vorhanden."))

    for group in groups:
        group_id = group.get("id") or ""
        rules = group.get("rules") or []
        if not rules:
            findings.append(ValidationFinding("warning", "empty_group", "Regelgruppe enthält keine Regeln.", groupId=group_id))
            continue

        for rule in rules:
            rule_id = rule.get("id") or ""
            active = bool(rule.get("active"))
            dimension = rule.get("dimension") or ""
            message = rule.get("message") or ""
            condition = rule.get("condition") or ""
            rule_type = rule.get("ruleType") or "custom"

            if active and not dimension:
                findings.append(
                    ValidationFinding("warning", "missing_dimension", "Aktive Regel braucht eine fachliche Dimension.", groupId=group_id, ruleId=rule_id)
                )
            if dimension and dimension not in known_dimensions:
                findings.append(
                    ValidationFinding("warning", "unknown_dimension", f"Unbekannte Dimension: {dimension}", groupId=group_id, ruleId=rule_id)
                )
            if active and not message.strip():
                findings.append(
                    ValidationFinding("warning", "missing_message", "Aktive Regel braucht eine Fehlermeldung.", groupId=group_id, ruleId=rule_id)
                )
            if active and not condition.strip():
                findings.append(
                    ValidationFinding("error", "missing_condition", "Aktive Regel braucht eine Bedingung.", groupId=group_id, ruleId=rule_id)
                )
            if rule_type not in known_rule_types:
                findings.append(
                    ValidationFinding("info", "unknown_rule_type", f"Regeltyp ist noch nicht im Katalog: {rule_type}", groupId=group_id, ruleId=rule_id)
                )

    severities = Counter(finding.severity for finding in findings)
    return {
        "ok": not any(finding.severity == "error" for finding in findings),
        "counts": dict(severities),
        "findings": [finding.to_dict() for finding in findings],
    }


def normalize_editor_model(model: Dict[str, Any]) -> Dict[str, Any]:
    normalize_editor_rules(model)
    summarize_editor_model(model)
    model["validation"] = validate_editor_model(model)
    return model
