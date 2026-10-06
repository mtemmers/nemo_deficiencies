import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Mapping


BUILTIN_PLACEHOLDERS = {"field", "displayName", "description"}
PARAMETER_TYPES = {"integer", "number", "string", "regex", "boolean", "enum"}
PLACEHOLDER_PATTERN = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)\}(?!\})")
SQL_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class RuleTemplateValidationError(ValueError):
    pass


class RuleTemplateResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedCatalogRule:
    templateId: str
    templateVersion: int
    condition: str
    messageDe: str
    messageEn: str
    dimension: str
    ruleType: str
    parameters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "templateId": self.templateId,
            "templateVersion": self.templateVersion,
            "condition": self.condition,
            "messageDe": self.messageDe,
            "messageEn": self.messageEn,
            "dimension": self.dimension,
            "ruleType": self.ruleType,
            "parameters": dict(self.parameters),
        }


def validate_rule_template(
    condition_template: str,
    message_de_template: str,
    message_en_template: str,
    parameter_schema: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    condition_template = str(condition_template or "").strip()
    if not condition_template:
        raise RuleTemplateValidationError("Die Bedingungsvorlage darf nicht leer sein.")
    placeholders = _placeholders(condition_template, message_de_template, message_en_template)
    if "field" not in _placeholders(condition_template):
        raise RuleTemplateValidationError("Die Bedingungsvorlage muss den Platzhalter {field} enthalten.")

    schema = dict(parameter_schema or {})
    for name, definition in schema.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(name)):
            raise RuleTemplateValidationError(f"Ungültiger Parametername: {name}")
        if name in BUILTIN_PLACEHOLDERS:
            raise RuleTemplateValidationError(f"Der reservierte Platzhalter {{{name}}} darf nicht als Parameter definiert werden.")
        if not isinstance(definition, Mapping):
            raise RuleTemplateValidationError(f"Die Definition für {{{name}}} muss ein Objekt sein.")
        parameter_type = str(definition.get("type") or "").strip()
        if parameter_type not in PARAMETER_TYPES:
            raise RuleTemplateValidationError(f"Unbekannter Parametertyp für {{{name}}}: {parameter_type}")
        if parameter_type == "enum" and not list(definition.get("choices") or []):
            raise RuleTemplateValidationError(f"Der Enum-Parameter {{{name}}} benötigt choices.")
        if "default" in definition:
            _validate_parameter_value(name, definition["default"], definition, RuleTemplateValidationError)

    unknown = placeholders - BUILTIN_PLACEHOLDERS - set(schema)
    if unknown:
        names = ", ".join(f"{{{name}}}" for name in sorted(unknown))
        raise RuleTemplateValidationError(f"Nicht definierte Platzhalter: {names}")
    unused = set(schema) - placeholders
    if unused:
        names = ", ".join(sorted(unused))
        raise RuleTemplateValidationError(f"Nicht verwendete Parameter: {names}")


def resolve_rule_template(
    template_version: Any,
    *,
    field: str,
    display_name: str = "",
    description: str = "",
    parameters: Mapping[str, Any] | None = None,
) -> ResolvedCatalogRule:
    condition_template = str(_value(template_version, "conditionTemplate") or "")
    message_de_template = str(_value(template_version, "messageDeTemplate") or "")
    message_en_template = str(_value(template_version, "messageEnTemplate") or "")
    parameter_schema = dict(_value(template_version, "parameterSchema") or {})
    validate_rule_template(
        condition_template,
        message_de_template,
        message_en_template,
        parameter_schema,
    )

    field = str(field or "").strip()
    if not SQL_IDENTIFIER_PATTERN.fullmatch(field):
        raise RuleTemplateResolutionError("Der Internalname ist kein sicherer SQL-Feldname.")

    supplied = dict(parameters or {})
    unknown_parameters = set(supplied) - set(parameter_schema)
    if unknown_parameters:
        names = ", ".join(sorted(unknown_parameters))
        raise RuleTemplateResolutionError(f"Unbekannte Parameter: {names}")

    resolved_parameters: Dict[str, Any] = {}
    for name, definition in parameter_schema.items():
        if name in supplied:
            value = supplied[name]
        elif "default" in definition:
            value = definition["default"]
        elif bool(definition.get("required", True)):
            raise RuleTemplateResolutionError(f"Der Parameter {{{name}}} fehlt.")
        else:
            value = ""
        resolved_parameters[name] = _validate_parameter_value(
            name,
            value,
            definition,
            RuleTemplateResolutionError,
        )

    text_context: Dict[str, Any] = {
        "field": field,
        "displayName": str(display_name or field),
        "description": str(description or ""),
        **resolved_parameters,
    }
    sql_context = {
        "field": field,
        "displayName": _sql_literal(text_context["displayName"]),
        "description": _sql_literal(text_context["description"]),
        **{
            name: _sql_parameter(value, parameter_schema[name])
            for name, value in resolved_parameters.items()
        },
    }
    return ResolvedCatalogRule(
        templateId=str(_value(template_version, "templateId") or ""),
        templateVersion=int(_value(template_version, "version") or 0),
        condition=_replace_placeholders(condition_template, sql_context),
        messageDe=_replace_placeholders(message_de_template, text_context),
        messageEn=_replace_placeholders(message_en_template, text_context),
        dimension=str(_value(template_version, "dimension") or ""),
        ruleType=str(_value(template_version, "ruleType") or "custom"),
        parameters=resolved_parameters,
    )


def _placeholders(*templates: str) -> set[str]:
    return {
        match.group(1)
        for template in templates
        for match in PLACEHOLDER_PATTERN.finditer(str(template or ""))
    }


def _replace_placeholders(template: str, values: Mapping[str, Any]) -> str:
    def replacement(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise RuleTemplateResolutionError(f"Der Platzhalter {{{name}}} kann nicht aufgelöst werden.")
        return str(values[name])

    return PLACEHOLDER_PATTERN.sub(replacement, str(template or ""))


def _validate_parameter_value(
    name: str,
    value: Any,
    definition: Mapping[str, Any],
    error_type: type[ValueError],
) -> Any:
    parameter_type = str(definition.get("type") or "")
    try:
        if parameter_type == "integer":
            if isinstance(value, bool) or isinstance(value, float) and not value.is_integer():
                raise ValueError
            normalized: Any = int(value)
        elif parameter_type == "number":
            if isinstance(value, bool):
                raise ValueError
            normalized = float(Decimal(str(value)))
        elif parameter_type == "boolean":
            if isinstance(value, bool):
                normalized = value
            elif str(value).strip().casefold() in {"true", "1", "yes", "ja"}:
                normalized = True
            elif str(value).strip().casefold() in {"false", "0", "no", "nein"}:
                normalized = False
            else:
                raise ValueError
        else:
            normalized = str(value)
    except (ValueError, TypeError, InvalidOperation) as exc:
        raise error_type(f"Ungültiger Wert für {{{name}}} ({parameter_type}).") from exc

    if parameter_type in {"integer", "number"}:
        numeric_value = Decimal(str(normalized))
        if "min" in definition and numeric_value < Decimal(str(definition["min"])):
            raise error_type(f"{{{name}}} muss mindestens {definition['min']} sein.")
        if "max" in definition and numeric_value > Decimal(str(definition["max"])):
            raise error_type(f"{{{name}}} darf höchstens {definition['max']} sein.")
    if parameter_type in {"string", "regex", "enum"}:
        if bool(definition.get("required", True)) and not normalized:
            raise error_type(f"Der Parameter {{{name}}} darf nicht leer sein.")
        choices = [str(choice) for choice in definition.get("choices") or []]
        if parameter_type == "enum" and normalized not in choices:
            raise error_type(f"{{{name}}} muss einer der erlaubten Auswahlwerte sein.")
    return normalized


def _sql_parameter(value: Any, definition: Mapping[str, Any]) -> str:
    parameter_type = str(definition.get("type") or "")
    if parameter_type == "integer":
        return str(value)
    if parameter_type == "number":
        return format(Decimal(str(value)), "f")
    if parameter_type == "boolean":
        return "TRUE" if value else "FALSE"
    return _sql_literal(str(value))


def _sql_literal(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _value(source: Any, name: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(name)
    return getattr(source, name, None)
