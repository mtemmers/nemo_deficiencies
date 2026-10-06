from typing import Any, Dict, Iterable


def _text(value: Any) -> str:
    return str(value or "").strip()


def build_config_statistics(
    report_models: Iterable[Dict[str, Any]],
    skipped_reports: Iterable[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    reports = []
    distinct_fields = set()
    dimension_counts: Dict[str, int] = {}
    rule_type_counts: Dict[str, int] = {}

    for item in report_models:
        report = dict(item.get("report") or {})
        model = item.get("model") or {}
        groups = list(((model.get("checks") or {}).get("groups") or []))
        rule_count = 0
        active_rule_count = 0
        report_groups = []

        for group in groups:
            field_name = _text(
                group.get("internalName")
                or group.get("field")
                or group.get("displayName")
                or group.get("title")
            )
            if field_name:
                distinct_fields.add(field_name.casefold())
            rules = list(group.get("rules") or [])
            rule_count += len(rules)
            active_rule_count += sum(1 for rule in rules if bool(rule.get("active")))
            report_rules = []
            for rule in rules:
                dimension = _text(rule.get("dimension")) or "Ohne Typ"
                rule_type = _text(rule.get("ruleType")) or "custom"
                dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
                rule_type_counts[rule_type] = rule_type_counts.get(rule_type, 0) + 1
                report_rules.append(
                    {
                        "id": _text(rule.get("id")),
                        "message": _text(rule.get("message")) or "Ohne Fehlermeldung",
                        "condition": _text(rule.get("condition")),
                        "dimension": dimension,
                        "ruleType": rule_type,
                        "active": bool(rule.get("active")),
                    }
                )
            report_groups.append(
                {
                    "id": _text(group.get("id")),
                    "displayName": _text(group.get("displayName") or group.get("title") or field_name),
                    "internalName": field_name,
                    "description": _text(group.get("description")),
                    "ruleCount": len(report_rules),
                    "activeRuleCount": sum(1 for rule in report_rules if rule["active"]),
                    "inactiveRuleCount": sum(1 for rule in report_rules if not rule["active"]),
                    "rules": report_rules,
                }
            )

        report_id = str(
            report.get("internalName")
            or report.get("id")
            or report.get("displayName")
            or ""
        ).strip()
        reports.append(
            {
                "id": report_id,
                "displayName": report.get("displayName") or report_id,
                "internalName": report.get("internalName") or report_id,
                "source": item.get("source") or "report",
                "groupCount": len(groups),
                "ruleCount": rule_count,
                "activeRuleCount": active_rule_count,
                "inactiveRuleCount": rule_count - active_rule_count,
                "groups": report_groups,
            }
        )

    reports.sort(key=lambda item: str(item["displayName"]).casefold())
    skipped = list(skipped_reports)
    group_count = sum(item["groupCount"] for item in reports)
    rule_count = sum(item["ruleCount"] for item in reports)
    active_rule_count = sum(item["activeRuleCount"] for item in reports)

    return {
        "summary": {
            "reportCount": len(reports),
            "groupCount": group_count,
            "distinctFieldCount": len(distinct_fields),
            "ruleCount": rule_count,
            "activeRuleCount": active_rule_count,
            "inactiveRuleCount": rule_count - active_rule_count,
            "draftReportCount": sum(1 for item in reports if item["source"] == "draft"),
            "skippedReportCount": len(skipped),
        },
        "reports": reports,
        "dimensions": [
            {"name": name, "count": count}
            for name, count in sorted(dimension_counts.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "ruleTypes": [
            {"name": name, "count": count}
            for name, count in sorted(rule_type_counts.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "skippedReports": skipped,
    }
