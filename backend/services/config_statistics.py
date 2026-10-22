from typing import Any, Dict, Iterable


def _rule_detail(rule: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(rule.get("id") or ""),
        "message": str(rule.get("message") or ""),
        "condition": str(rule.get("condition") or ""),
        "dimension": str(rule.get("dimension") or ""),
        "ruleType": str(rule.get("ruleType") or ""),
        "active": bool(rule.get("active")),
    }


def build_config_statistics(
    report_models: Iterable[Dict[str, Any]],
    skipped_reports: Iterable[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    reports = []
    distinct_fields = set()
    dimension_counts: Dict[str, int] = {}

    for item in report_models:
        report = dict(item.get("report") or {})
        model = item.get("model") or {}
        groups = list(((model.get("checks") or {}).get("groups") or []))
        rule_count = 0
        active_rule_count = 0
        group_details = []

        for group in groups:
            field_name = str(
                group.get("internalName")
                or group.get("field")
                or group.get("displayName")
                or group.get("title")
                or ""
            ).strip()
            if field_name:
                distinct_fields.add(field_name.casefold())
            rules = list(group.get("rules") or [])
            rule_count += len(rules)
            active_rule_count += sum(1 for rule in rules if bool(rule.get("active")))
            rule_details = [_rule_detail(rule) for rule in rules]
            for rule in rule_details:
                dimension = rule["dimension"] or "Ohne Typ"
                dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
            group_details.append(
                {
                    "id": str(group.get("id") or ""),
                    "displayName": str(group.get("displayName") or group.get("title") or field_name),
                    "internalName": str(group.get("internalName") or group.get("field") or ""),
                    "description": str(group.get("description") or ""),
                    "ruleCount": len(rule_details),
                    "activeRuleCount": sum(1 for rule in rule_details if rule["active"]),
                    "rules": rule_details,
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
                "groups": group_details,
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
        "dimensions": [{"name": name, "count": count} for name, count in sorted(dimension_counts.items())],
        "reports": reports,
        "skippedReports": skipped,
    }
