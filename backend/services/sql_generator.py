import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from backend.services.sql_model import (
    alias_from_expression,
    clean_condition,
    find_final_select_start,
    infer_rule_dimension,
    normalize_editor_model,
    normalize_rule_message,
)


class SqlGenerationError(ValueError):
    pass


@dataclass(frozen=True)
class CteRange:
    start: int
    open_paren: int
    close_paren: int
    end: int


@dataclass(frozen=True)
class SqlRenderResult:
    sql: str
    generated_checks_sql: str
    original_checks_sql: str
    changed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sql": self.sql,
            "generatedChecksSql": self.generated_checks_sql,
            "originalChecksSql": self.original_checks_sql,
            "changed": self.changed,
        }


def render_top_25_sql(sql: str) -> str:
    final_select_start = find_final_select_start(sql)
    if final_select_start is None:
        raise SqlGenerationError("Das finale SELECT für den TOP-25-Bericht wurde nicht gefunden.")

    prefix = sql[:final_select_start]
    final_select = sql[final_select_start:]
    final_select = re.sub(
        r"(?i)\bSELECT\b(?:\s+TOP\s+\d+)?",
        "SELECT TOP 25",
        final_select,
        count=1,
    )
    order_matches = list(re.finditer(r"(?im)^\s*ORDER\s+BY\s+[^\r\n;]+;?\s*$", final_select))
    if order_matches:
        last_order = order_matches[-1]
        final_select = final_select[: last_order.start()] + final_select[last_order.end() :]

    final_select = final_select.rstrip().removesuffix(";").rstrip()
    return f"{prefix}{final_select}\nORDER BY ERROREVALUATION DESC\n"


def render_sql_from_model(original_sql: str, editor_model: Dict[str, Any]) -> SqlRenderResult:
    model = normalize_editor_model(editor_model)
    new_source_attributes = missing_source_attributes(original_sql, model)
    sql_with_source = apply_source_attributes(original_sql, model)
    sql_with_source = append_attributes_to_description2(sql_with_source, new_source_attributes)
    cte_range = find_checks_cte(sql_with_source)
    original_checks_sql = ""
    if cte_range:
        original_checks_sql = sql_with_source[cte_range.start:cte_range.end]

    generated_checks_sql = render_checks_cte(model, original_checks_sql)
    if cte_range:
        sql_body = sql_with_source[: cte_range.start] + generated_checks_sql + sql_with_source[cte_range.end :]
    else:
        if not sql_with_source.strip():
            sql_body = generated_checks_sql
        else:
            sql_body = sql_with_source.rstrip() + "\n\n" + generated_checks_sql + "\n"
    sql_body = apply_source_settings(sql_body, model)
    sql = apply_generated_header(sql_body, model)

    return SqlRenderResult(
        sql=sql,
        generated_checks_sql=generated_checks_sql,
        original_checks_sql=original_checks_sql,
        changed=normalize_sql(sql) != normalize_sql(original_sql),
    )


def render_checks_cte(editor_model: Dict[str, Any], original_checks_sql: str = "") -> str:
    groups = ((editor_model.get("checks") or {}).get("groups") or [])
    language = report_language(editor_model)
    from_clause = extract_from_clause(original_checks_sql) or "joined j"
    projection = extract_projection(original_checks_sql, from_clause)

    lines = [
        "checks AS (",
        "    SELECT",
        f"        {projection},",
        "        (",
    ]

    if groups:
        for group_index, group in enumerate(groups):
            if group_index:
                lines.append("            ||")
            lines.extend(render_group_case(group, language))
    else:
        lines.extend([
            "            CASE",
            "                ELSE ''",
            "            END",
        ])

    lines.extend([
        "        ) AS DEFICIENCY_DESCRIPTION",
        "    FROM",
    ])
    lines.extend(render_from_clause(from_clause))
    lines.append(")")
    return "\n".join(lines)


def render_group_case(group: Dict[str, Any], language: str = "legacy") -> list[str]:
    number = group.get("number") or 0
    title = clean_comment(group.get("displayName") or group.get("title") or (f"Check {number}" if language == "en" else f"Prüfung {number}"))
    description = clean_comment(group.get("description") or "")
    field = clean_comment(group.get("field") or "")
    type_hints = [clean_comment(value) for value in (group.get("typeHints") or []) if clean_comment(value)]
    if not type_hints:
        type_hints = sorted({rule_dimension(rule) for rule in (group.get("rules") or []) if rule_dimension(rule)})

    lines = [
        "            -- ================================================================",
        f"            -- {'CHECK' if language == 'en' else 'PRÜFUNG'} {number}: {title}" if number else f"            -- {title}",
    ]
    if description:
        lines.append(f"            -- {description}")
    if field:
        lines.append(f"            -- {field}")
    if type_hints:
        lines.append(f"            -- {'Types' if language == 'en' else 'Typen'}: {', '.join(localize_dimension(value, language) for value in type_hints)}")
    lines.append("            CASE")

    rules = group.get("rules") or []
    for rule in rules:
        lines.extend(render_rule(rule, language))

    lines.extend([
        "                ELSE ''",
        "            END",
    ])
    return lines


def render_rule(rule: Dict[str, Any], language: str = "legacy") -> list[str]:
    condition = clean_condition(str(rule.get("condition") or ""))
    message = normalize_rule_message(str(rule.get("message") or ""))
    dimension = rule_dimension(rule)
    active = bool(rule.get("active"))
    lines: list[str] = []

    if dimension:
        lines.append(f"                -- {localize_dimension(dimension, language)}")
    if not condition:
        lines.append(
            "                -- Rule without a condition was not generated"
            if language == "en"
            else "                -- Regel ohne Bedingung wurde nicht generiert"
        )
        return lines

    lines.append(f"                WHEN {condition}")
    if active:
        lines.append(f"                    THEN {sql_literal(sql_message(message))}")
    elif message:
        lines.append(f"                    THEN '' --{sql_literal(sql_message(message))}")
    else:
        lines.append("                    THEN ''")
    return lines


def rule_dimension(rule: Dict[str, Any]) -> str:
    condition = clean_condition(str(rule.get("condition") or ""))
    message = normalize_rule_message(str(rule.get("message") or ""))
    rule_type = str(rule.get("ruleType") or "")
    return clean_comment(rule.get("dimension") or "") or infer_rule_dimension(condition, message, rule_type)


def sql_message(message: str) -> str:
    clean = normalize_rule_message(message)
    return f"|{clean}" if clean else ""


def apply_generated_header(sql: str, editor_model: Dict[str, Any]) -> str:
    header = render_sql_header(editor_model)
    body = strip_leading_comment_header(sql)
    return header + "\n" + body.lstrip()


def render_sql_header(editor_model: Dict[str, Any]) -> str:
    language = report_language(editor_model)
    report = editor_model.get("report") or {}
    summary = editor_model.get("summary") or {}
    groups = ((editor_model.get("checks") or {}).get("groups") or [])
    rules = [rule for group in groups for rule in group.get("rules", [])]
    dimension_counts = count_dimensions(rules)
    report_name = clean_comment(
        report.get("displayName")
        or report.get("internalName")
        or report.get("id")
        or ("Unnamed report" if language == "en" else "Unbenannter Report")
    )
    internal_name = clean_comment(report.get("internalName") or "")

    lines = [
        "-- ================================================================================",
        "-- NEMO DQM Report SQL",
        f"-- Report: {report_name}",
    ]
    if internal_name:
        lines.append(f"-- Internal Name: {internal_name}")
    lines.extend([
        f"-- {('Generated at' if language == 'en' else 'Generiert am') if language != 'legacy' else 'Generated At'}: {generated_timestamp()}",
        "-- Generator: nemo_deficiencies SQL generator",
        f"-- {'Check groups' if language == 'en' else 'Prüfblöcke'}: {summary.get('checkGroupCount', len(groups))}",
        f"-- {'Rules active/inactive' if language == 'en' else 'Regeln aktiv/inaktiv'}: {summary.get('activeRuleCount', 0)} / {summary.get('inactiveRuleCount', 0)}",
        f"-- {'DQ dimensions' if language == 'en' else 'DQ-Typen'}: {format_dimension_counts(dimension_counts, language)}",
        "-- --------------------------------------------------------------------------------",
        "-- Checks:",
    ])
    for group in groups:
        lines.append(format_group_header_line(group, language))
    lines.append("-- ================================================================================")
    return "\n".join(lines)


def generated_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def strip_leading_comment_header(sql: str) -> str:
    match = re.search(r"(?im)^\s*WITH\b", sql)
    if not match:
        return sql
    prefix = sql[: match.start()]
    if all(not line.strip() or line.strip().startswith("--") for line in prefix.splitlines()):
        return sql[match.start():]
    return sql


def count_dimensions(rules: list[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for rule in rules:
        dimension = rule_dimension(rule) or "Ohne Typ"
        counts[dimension] = counts.get(dimension, 0) + 1
    return counts


def format_dimension_counts(counts: Dict[str, int], language: str = "legacy") -> str:
    if not counts:
        return "none" if language == "en" else "keine"
    order = [
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
        "Ohne Typ",
    ]
    parts = [f"{localize_dimension(name, language)}={counts[name]}" for name in order if name in counts]
    parts.extend(f"{localize_dimension(name, language)}={count}" for name, count in sorted(counts.items()) if name not in order)
    return ", ".join(parts)


def format_group_header_line(group: Dict[str, Any], language: str = "legacy") -> str:
    number = group.get("number") or 0
    title = clean_comment(group.get("title") or (f"Check {number}" if language == "en" else f"Prüfung {number}"))
    rules = group.get("rules") or []
    active = sum(1 for rule in rules if bool(rule.get("active")))
    inactive = len(rules) - active
    dimensions = sorted({rule_dimension(rule) for rule in rules if rule_dimension(rule)})
    dimension_text = ", ".join(localize_dimension(value, language) for value in dimensions) if dimensions else ("without type" if language == "en" else "ohne Typ")
    state_text = f"{active} active / {inactive} inactive" if language == "en" else f"{active} aktiv / {inactive} inaktiv"
    return f"--   {number:02d}. {title} ({state_text}) - {dimension_text}"


def report_language(editor_model: Dict[str, Any]) -> str:
    value = str(editor_model.get("reportLanguage") or "").casefold()
    return value if value in {"de", "en"} else "legacy"


def localize_dimension(value: str, language: str) -> str:
    if language != "en":
        return value
    return {
        "Vollständigkeit": "Completeness",
        "Validität": "Validity",
        "Korrektheit": "Correctness",
        "Eindeutigkeit": "Uniqueness",
        "Konsistenz": "Consistency",
        "Aktualität": "Timeliness",
        "Genauigkeit": "Accuracy",
        "Redundanz": "Redundancy",
        "Einheitlichkeit": "Uniformity",
        "Relevanz": "Relevance",
        "Zuverlässigkeit": "Reliability",
        "Verständlichkeit": "Understandability",
        "Ohne Typ": "Without type",
    }.get(value, value)

def find_checks_cte(sql: str) -> Optional[CteRange]:
    match = re.search(r"(?im)^\s*checks\s+AS\s*\(", sql)
    if not match:
        return None
    open_paren = sql.rfind("(", match.start(), match.end())
    if open_paren == -1:
        raise SqlGenerationError("checks-CTE hat keine öffnende Klammer.")
    close_paren = find_matching_paren(sql, open_paren)
    if close_paren is None:
        raise SqlGenerationError("checks-CTE konnte nicht bis zur schließenden Klammer gelesen werden.")
    return CteRange(start=match.start(), open_paren=open_paren, close_paren=close_paren, end=close_paren + 1)


def apply_source_settings(sql: str, editor_model: Dict[str, Any]) -> str:
    source = editor_model.get("source") or {}
    subtype = str(source.get("masterDataSubType") or "").strip()
    exceptions = source.get("exceptions") or []
    source_block = next((block for block in (editor_model.get("blocks") or []) if block.get("id") == "source"), None)
    cte_name = str((source_block or {}).get("cteName") or "").strip()
    if not cte_name or (not subtype and not exceptions):
        return sql

    cte_range = find_named_cte(sql, cte_name)
    if not cte_range:
        raise SqlGenerationError(f"Quellblock '{cte_name}' wurde im SQL nicht gefunden.")
    inner = sql[cte_range.open_paren + 1 : cte_range.close_paren]

    subtype_pattern = re.compile(
        r"(?is)(UPPER\s*\(\s*TRIM\s*\(\s*MASTER_DATA_SUB_TYPE\s*\)\s*\)\s*=\s*)'((?:''|[^'])*)'"
    )
    subtype_match = subtype_pattern.search(inner)
    if subtype and not subtype_match:
        raise SqlGenerationError("MASTER_DATA_SUB_TYPE-Filter wurde im Quellblock nicht gefunden.")

    exception_pattern = re.compile(
        r"(?is)\s+AND\s+[A-Za-z_][\w]*\s+NOT\s+IN\s*\((?:[^()]|'(?:''|[^'])*')*\)"
    )
    inner = exception_pattern.sub("", inner)
    if subtype:
        inner = subtype_pattern.sub(lambda match: f"{match.group(1)}{sql_literal(subtype)}", inner, count=1)

    rendered_exceptions = [render_source_exception(exception) for exception in exceptions]
    if rendered_exceptions:
        insertion_match = subtype_pattern.search(inner)
        if not insertion_match:
            raise SqlGenerationError("Ausnahmen benötigen einen MASTER_DATA_SUB_TYPE-Filter im Quellblock.")
        exception_sql = "".join(f"\n        AND {condition}" for condition in rendered_exceptions)
        inner = inner[: insertion_match.end()] + exception_sql + inner[insertion_match.end() :]

    suffix = sql[cte_range.close_paren :]
    legacy_separator = re.search(r"(?m)^\s*,\s*$", suffix)
    if legacy_separator:
        legacy_tail = exception_pattern.sub("", suffix[: legacy_separator.start()])
        suffix = legacy_tail + suffix[legacy_separator.start() :]
    return sql[: cte_range.open_paren + 1] + inner + suffix


def apply_source_attributes(sql: str, editor_model: Dict[str, Any]) -> str:
    source = editor_model.get("source") or {}
    attributes = source.get("attributes") or []
    source_block = next((block for block in (editor_model.get("blocks") or []) if block.get("id") == "source"), None)
    cte_name = str((source_block or {}).get("cteName") or "").strip()
    if not cte_name or not attributes:
        return sql

    cte_range = find_named_cte(sql, cte_name)
    if not cte_range:
        raise SqlGenerationError(f"Quellblock '{cte_name}' wurde im SQL nicht gefunden.")
    inner = sql[cte_range.open_paren + 1 : cte_range.close_paren]
    select_pos = find_top_level_keyword(inner, "SELECT")
    from_pos = find_top_level_keyword(inner, "FROM", select_pos + len("SELECT") if select_pos is not None else 0)
    if select_pos is None or from_pos is None:
        raise SqlGenerationError(f"SELECT-Liste im Quellblock '{cte_name}' wurde nicht gefunden.")

    projection_start = select_pos + len("SELECT")
    projection = inner[projection_start:from_pos]
    projected_names = {
        alias_from_expression(expression).upper()
        for expression in split_top_level_projection(projection)
        if alias_from_expression(expression)
    }
    missing: list[str] = []
    for attribute in attributes:
        name = str(attribute.get("name") or "").strip()
        if not name or name.upper() in projected_names:
            continue
        if not re.fullmatch(r"[A-Za-z_][\w]*", name):
            raise SqlGenerationError(f"Ungültiges Quellattribut: {name}")
        missing.append(name)
    if not missing:
        return sql

    base = projection.rstrip()
    trailing = projection[len(base):]
    separator = ""
    last_line_start = base.rfind("\n") + 1
    last_line_comment = base.find("--", last_line_start)
    if last_line_comment >= 0:
        before_comment = base[:last_line_comment]
        if not before_comment.rstrip().endswith(","):
            whitespace = before_comment[len(before_comment.rstrip()):]
            base = before_comment.rstrip() + "," + whitespace + base[last_line_comment:]
    elif not base.endswith(","):
        separator = ","
    additions = "".join(f"\n        {name}{',' if index < len(missing) - 1 else ''}" for index, name in enumerate(missing))
    rendered_projection = base + separator + additions + trailing
    rendered_inner = inner[:projection_start] + rendered_projection + inner[from_pos:]
    return sql[: cte_range.open_paren + 1] + rendered_inner + sql[cte_range.close_paren:]


def missing_source_attributes(sql: str, editor_model: Dict[str, Any]) -> list[Dict[str, Any]]:
    source = editor_model.get("source") or {}
    attributes = source.get("attributes") or []
    source_block = next((block for block in (editor_model.get("blocks") or []) if block.get("id") == "source"), None)
    cte_name = str((source_block or {}).get("cteName") or "").strip()
    if not cte_name or not attributes:
        return []

    cte_range = find_named_cte(sql, cte_name)
    if not cte_range:
        return []
    inner = sql[cte_range.open_paren + 1 : cte_range.close_paren]
    select_pos = find_top_level_keyword(inner, "SELECT")
    from_pos = find_top_level_keyword(inner, "FROM", select_pos + len("SELECT") if select_pos is not None else 0)
    if select_pos is None or from_pos is None:
        return []

    projection = inner[select_pos + len("SELECT") : from_pos]
    projected_names = {
        alias_from_expression(expression).upper()
        for expression in split_top_level_projection(projection)
        if alias_from_expression(expression)
    }
    return [
        attribute
        for attribute in attributes
        if str(attribute.get("name") or "").strip()
        and str(attribute.get("name") or "").strip().upper() not in projected_names
    ]


def append_attributes_to_description2(sql: str, attributes: list[Dict[str, Any]]) -> str:
    if not attributes:
        return sql

    final_select_start = find_final_select_start(sql)
    if final_select_start is None:
        return sql
    segment = sql[final_select_start:]
    select_pos = find_top_level_keyword(segment, "SELECT")
    from_pos = find_top_level_keyword(segment, "FROM", select_pos + len("SELECT") if select_pos is not None else 0)
    if select_pos is None or from_pos is None:
        return sql

    projection_start = select_pos + len("SELECT")
    projection = segment[projection_start:from_pos]
    description_span: Optional[tuple[int, int]] = None
    description_expression = ""
    for start, end in top_level_projection_spans(projection):
        raw_expression = projection[start:end]
        expression_without_comments = re.sub(r"(?m)^\s*--[^\n]*(?:\n|$)", "", raw_expression).strip()
        if alias_from_expression(expression_without_comments).upper() != "DESCRIPTION2":
            continue
        alias_match = re.match(r"(?is)(?P<expression>.*)\s+AS\s+DESCRIPTION2\s*$", expression_without_comments)
        if alias_match:
            description_span = (start, end)
            description_expression = alias_match.group("expression").strip()
        break
    if not description_span or not description_expression:
        return sql

    detail_parts: list[str] = []
    for attribute in attributes:
        name = str(attribute.get("name") or "").strip()
        if not re.fullmatch(r"[A-Za-z_][\w]*", name):
            raise SqlGenerationError(f"Ungültiges Quellattribut: {name}")
        label = clean_detail_label(attribute.get("displayName") or attribute.get("comment") or name)
        detail_parts.append(
            f"            {sql_literal(f'|<{label}>')} || COALESCE(TO_NVARCHAR({name}), '')"
        )

    joined_details = " ||\n".join(detail_parts)
    rendered_expression = (
        "\n    REPLACE_REGEXPR(\n"
        "        '\\\\s+' IN TRIM(\n"
        f"            COALESCE(TO_NVARCHAR({description_expression}), '') ||\n"
        f"{joined_details}\n"
        "        ) WITH ' '\n"
        "    ) AS DESCRIPTION2"
    )
    start, end = description_span
    rendered_projection = projection[:start] + rendered_expression + projection[end:]
    rendered_segment = segment[:projection_start] + rendered_projection + segment[from_pos:]
    return sql[:final_select_start] + rendered_segment


def clean_detail_label(value: Any) -> str:
    label = re.sub(r"\s+", " ", str(value or "")).strip()
    if label.startswith("#ERP-Origin:"):
        label = label.split(".")[-1].strip()
    return label or "Feld"


def top_level_projection_spans(projection: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    start = 0
    index = 0
    while index < len(projection):
        current = projection[index]
        nxt = projection[index + 1] if index + 1 < len(projection) else ""
        if in_line_comment:
            if current == "\n":
                in_line_comment = False
            index += 1
            continue
        if in_block_comment:
            if current == "*" and nxt == "/":
                in_block_comment = False
                index += 2
                continue
            index += 1
            continue
        if in_string:
            if current == "'":
                if nxt == "'":
                    index += 2
                    continue
                in_string = False
            index += 1
            continue
        if current == "-" and nxt == "-":
            in_line_comment = True
            index += 2
            continue
        if current == "/" and nxt == "*":
            in_block_comment = True
            index += 2
            continue
        if current == "'":
            in_string = True
        elif current == "(":
            depth += 1
        elif current == ")":
            depth = max(0, depth - 1)
        elif current == "," and depth == 0:
            spans.append((start, index))
            start = index + 1
        index += 1
    spans.append((start, len(projection)))
    return spans


def split_top_level_projection(projection: str) -> list[str]:
    expressions: list[str] = []
    buffer: list[str] = []
    depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    index = 0
    while index < len(projection):
        current = projection[index]
        nxt = projection[index + 1] if index + 1 < len(projection) else ""
        if in_line_comment:
            if current == "\n":
                in_line_comment = False
                buffer.append(current)
            index += 1
            continue
        if in_block_comment:
            if current == "*" and nxt == "/":
                in_block_comment = False
                index += 2
                continue
            index += 1
            continue
        if in_string:
            buffer.append(current)
            if current == "'":
                if nxt == "'":
                    buffer.append(nxt)
                    index += 2
                    continue
                in_string = False
            index += 1
            continue
        if current == "-" and nxt == "-":
            in_line_comment = True
            index += 2
            continue
        if current == "/" and nxt == "*":
            in_block_comment = True
            index += 2
            continue
        if current == "'":
            in_string = True
            buffer.append(current)
        elif current == "(":
            depth += 1
            buffer.append(current)
        elif current == ")":
            depth = max(0, depth - 1)
            buffer.append(current)
        elif current == "," and depth == 0:
            expression = "".join(buffer).strip()
            if expression:
                expressions.append(expression)
            buffer = []
        else:
            buffer.append(current)
        index += 1
    expression = "".join(buffer).strip()
    if expression:
        expressions.append(expression)
    return expressions


def find_top_level_keyword(sql: str, keyword: str, start: int = 0) -> Optional[int]:
    depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    index = start
    keyword_upper = keyword.upper()
    while index < len(sql):
        current = sql[index]
        nxt = sql[index + 1] if index + 1 < len(sql) else ""
        if in_line_comment:
            if current == "\n":
                in_line_comment = False
            index += 1
            continue
        if in_block_comment:
            if current == "*" and nxt == "/":
                in_block_comment = False
                index += 2
                continue
            index += 1
            continue
        if in_string:
            if current == "'":
                if nxt == "'":
                    index += 2
                    continue
                in_string = False
            index += 1
            continue
        if current == "-" and nxt == "-":
            in_line_comment = True
            index += 2
            continue
        if current == "/" and nxt == "*":
            in_block_comment = True
            index += 2
            continue
        if current == "'":
            in_string = True
            index += 1
            continue
        if current == "(":
            depth += 1
        elif current == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and sql[index:index + len(keyword)].upper() == keyword_upper:
            before = sql[index - 1] if index else " "
            after_index = index + len(keyword)
            after = sql[after_index] if after_index < len(sql) else " "
            if not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_"):
                return index
        index += 1
    return None


def find_named_cte(sql: str, cte_name: str) -> Optional[CteRange]:
    match = re.search(rf"(?im)^\s*(?:WITH\s+)?{re.escape(cte_name)}\s+AS\s*\(", sql)
    if not match:
        return None
    open_paren = sql.rfind("(", match.start(), match.end())
    if open_paren == -1:
        raise SqlGenerationError(f"CTE '{cte_name}' hat keine öffnende Klammer.")
    close_paren = find_matching_paren(sql, open_paren)
    if close_paren is None:
        raise SqlGenerationError(f"CTE '{cte_name}' konnte nicht vollständig gelesen werden.")
    return CteRange(start=match.start(), open_paren=open_paren, close_paren=close_paren, end=close_paren + 1)


def render_source_exception(exception: Dict[str, Any]) -> str:
    field = str(exception.get("field") or "").strip()
    operator = str(exception.get("operator") or "NOT IN").strip().upper()
    values = [str(value) for value in (exception.get("values") or []) if str(value).strip()]
    if not re.fullmatch(r"[A-Za-z_][\w]*", field):
        raise SqlGenerationError(f"Ungültiges Ausnahmefeld: {field or '-'}")
    if operator != "NOT IN":
        raise SqlGenerationError(f"Nicht unterstützter Ausnahmeoperator: {operator}")
    if not values:
        raise SqlGenerationError(f"Ausnahme für {field} benötigt mindestens einen Wert.")
    return f"{field} NOT IN ({', '.join(sql_literal(value) for value in values)})"


def find_matching_paren(sql: str, open_paren: int) -> Optional[int]:
    depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    index = open_paren
    while index < len(sql):
        current = sql[index]
        nxt = sql[index + 1] if index + 1 < len(sql) else ""

        if in_line_comment:
            if current == "\n":
                in_line_comment = False
            index += 1
            continue

        if in_block_comment:
            if current == "*" and nxt == "/":
                in_block_comment = False
                index += 2
                continue
            index += 1
            continue

        if in_string:
            if current == "'":
                if nxt == "'":
                    index += 2
                    continue
                in_string = False
            index += 1
            continue

        if current == "-" and nxt == "-":
            in_line_comment = True
            index += 2
            continue
        if current == "/" and nxt == "*":
            in_block_comment = True
            index += 2
            continue
        if current == "'":
            in_string = True
            index += 1
            continue
        if current == "(":
            depth += 1
        elif current == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def extract_from_clause(original_checks_sql: str) -> str:
    inner = checks_inner(original_checks_sql)
    if not inner:
        return ""
    marker = re.search(r"(?is)\)\s+AS\s+DEFICIENCY_DESCRIPTION", inner)
    search_area = inner[marker.end() :] if marker else inner
    matches = list(re.finditer(r"(?im)^\s*FROM\b", search_area))
    if not matches:
        return ""
    from_text = search_area[matches[-1].end() :].strip()
    return strip_trailing_comma(from_text)


def extract_projection(original_checks_sql: str, from_clause: str) -> str:
    inner = checks_inner(original_checks_sql)
    if inner:
        match = re.search(r"(?is)\bSELECT\s+(?P<projection>[A-Za-z_][\w]*\.\*|\*)\s*,\s*\(", inner)
        if match:
            return match.group("projection")
    alias = extract_alias(from_clause)
    return f"{alias}.*" if alias else "*"


def checks_inner(original_checks_sql: str) -> str:
    cte_range = find_checks_cte(original_checks_sql) if original_checks_sql.strip() else None
    if not cte_range:
        return ""
    return original_checks_sql[cte_range.open_paren + 1 : cte_range.close_paren]


def extract_alias(from_clause: str) -> str:
    first_line = next((line.strip() for line in from_clause.splitlines() if line.strip()), "")
    tokens = re.split(r"\s+", first_line)
    if len(tokens) >= 2 and tokens[-1].isidentifier() and tokens[-1].upper() not in {"ON", "WHERE", "INNER", "LEFT", "RIGHT", "JOIN"}:
        return tokens[-1]
    return ""


def render_from_clause(from_clause: str) -> list[str]:
    lines = [line.rstrip() for line in from_clause.splitlines() if line.strip()]
    if not lines:
        return ["        joined j"]
    return ["        " + line.strip() for line in lines]


def strip_trailing_comma(text: str) -> str:
    stripped = text.strip()
    return stripped[:-1].rstrip() if stripped.endswith(",") else stripped


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def clean_comment(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().replace("--", "-")


def normalize_sql(sql: str) -> str:
    return "\n".join(line.rstrip() for line in sql.strip().splitlines())
