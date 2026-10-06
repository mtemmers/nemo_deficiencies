import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from backend.services.rule_catalog import validate_rule_template


RULE_TEMPLATE_STATUSES = {"draft", "approved", "deprecated"}
RULE_CANDIDATE_DECISIONS = {"rejected", "imported"}


class RuleCatalogError(RuntimeError):
    pass


class RuleTemplateNotFoundError(RuleCatalogError):
    pass


class RuleCatalogConflictError(RuleCatalogError):
    pass


@dataclass(frozen=True)
class RuleTemplateVersion:
    templateId: str
    version: int
    conditionTemplate: str
    messageDeTemplate: str
    messageEnTemplate: str
    dimension: str
    ruleType: str
    parameterSchema: Dict[str, Dict[str, Any]]
    compatibleDataTypes: list[str]
    fieldCategories: list[str]
    examples: list[Dict[str, Any]]
    changeNote: str
    createdAt: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "templateId": self.templateId,
            "version": self.version,
            "conditionTemplate": self.conditionTemplate,
            "messageDeTemplate": self.messageDeTemplate,
            "messageEnTemplate": self.messageEnTemplate,
            "dimension": self.dimension,
            "ruleType": self.ruleType,
            "parameterSchema": self.parameterSchema,
            "compatibleDataTypes": self.compatibleDataTypes,
            "fieldCategories": self.fieldCategories,
            "examples": self.examples,
            "changeNote": self.changeNote,
            "createdAt": self.createdAt,
        }


@dataclass(frozen=True)
class RuleCatalogTemplate:
    id: str
    key: str
    name: str
    description: str
    status: str
    currentVersion: int
    version: RuleTemplateVersion
    createdAt: str
    updatedAt: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "currentVersion": self.currentVersion,
            "version": self.version.to_dict(),
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }


@dataclass(frozen=True)
class RuleTemplateBinding:
    id: int
    templateId: str
    templateVersion: int
    configId: str
    project: str
    reportRef: str
    groupRef: str
    ruleRef: str
    parameters: Dict[str, Any]
    createdAt: str
    updatedAt: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "templateId": self.templateId,
            "templateVersion": self.templateVersion,
            "configId": self.configId,
            "project": self.project,
            "reportRef": self.reportRef,
            "groupRef": self.groupRef,
            "ruleRef": self.ruleRef,
            "parameters": self.parameters,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }


class RuleCatalogStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS rule_catalog_templates (
                    id TEXT PRIMARY KEY,
                    template_key TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    current_version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS rule_catalog_versions (
                    template_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    condition_template TEXT NOT NULL,
                    message_de_template TEXT NOT NULL DEFAULT '',
                    message_en_template TEXT NOT NULL DEFAULT '',
                    dimension TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    parameter_schema_json TEXT NOT NULL,
                    compatible_data_types_json TEXT NOT NULL,
                    field_categories_json TEXT NOT NULL,
                    examples_json TEXT NOT NULL,
                    change_note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(template_id, version),
                    FOREIGN KEY(template_id) REFERENCES rule_catalog_templates(id) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS rule_catalog_bindings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    template_version INTEGER NOT NULL,
                    config_id TEXT NOT NULL,
                    project TEXT NOT NULL,
                    report_ref TEXT NOT NULL,
                    group_ref TEXT NOT NULL,
                    rule_ref TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(config_id, project, report_ref, group_ref, rule_ref),
                    FOREIGN KEY(template_id, template_version)
                        REFERENCES rule_catalog_versions(template_id, version) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS rule_catalog_candidate_decisions (
                    config_id TEXT NOT NULL,
                    project TEXT NOT NULL,
                    candidate_key TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(config_id, project, candidate_key)
                );

                CREATE INDEX IF NOT EXISTS idx_rule_catalog_templates_status
                ON rule_catalog_templates(status, name);

                CREATE INDEX IF NOT EXISTS idx_rule_catalog_bindings_template
                ON rule_catalog_bindings(template_id, template_version);

                CREATE INDEX IF NOT EXISTS idx_rule_catalog_bindings_location
                ON rule_catalog_bindings(config_id, project, report_ref);

                CREATE INDEX IF NOT EXISTS idx_rule_catalog_candidate_decisions_scope
                ON rule_catalog_candidate_decisions(config_id, project, decision);
                """
            )

    def create_template(
        self,
        *,
        key: str,
        name: str,
        condition_template: str,
        message_de_template: str,
        message_en_template: str,
        dimension: str,
        rule_type: str,
        description: str = "",
        status: str = "draft",
        parameter_schema: Optional[Dict[str, Dict[str, Any]]] = None,
        compatible_data_types: Optional[list[str]] = None,
        field_categories: Optional[list[str]] = None,
        examples: Optional[list[Dict[str, Any]]] = None,
        change_note: str = "Initiale Version",
        template_id: Optional[str] = None,
    ) -> RuleCatalogTemplate:
        template_key = _template_key(key)
        template_name = str(name or "").strip()
        if not template_name:
            raise RuleCatalogError("Der Vorlagenname darf nicht leer sein.")
        status = _status(status)
        version_values = _version_values(
            condition_template,
            message_de_template,
            message_en_template,
            dimension,
            rule_type,
            parameter_schema,
            compatible_data_types,
            field_categories,
            examples,
            change_note,
        )
        template_id = str(template_id or f"rule_{uuid.uuid4().hex}")
        now = _utc_now()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO rule_catalog_templates (
                        id, template_key, name, description, status,
                        current_version, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    (template_id, template_key, template_name, str(description or "").strip(), status, now, now),
                )
                self._insert_version(connection, template_id, 1, version_values, now)
        except sqlite3.IntegrityError as exc:
            raise RuleCatalogConflictError(f"Die Regelvorlage '{template_key}' existiert bereits.") from exc
        return self.get_template(template_id)

    def add_version(
        self,
        template_ref: str,
        *,
        condition_template: str,
        message_de_template: str,
        message_en_template: str,
        dimension: str,
        rule_type: str,
        parameter_schema: Optional[Dict[str, Dict[str, Any]]] = None,
        compatible_data_types: Optional[list[str]] = None,
        field_categories: Optional[list[str]] = None,
        examples: Optional[list[Dict[str, Any]]] = None,
        change_note: str = "",
    ) -> RuleCatalogTemplate:
        current = self.get_template(template_ref)
        next_version = current.currentVersion + 1
        values = _version_values(
            condition_template,
            message_de_template,
            message_en_template,
            dimension,
            rule_type,
            parameter_schema,
            compatible_data_types,
            field_categories,
            examples,
            change_note,
        )
        now = _utc_now()
        with self._connect() as connection:
            self._insert_version(connection, current.id, next_version, values, now)
            connection.execute(
                """
                UPDATE rule_catalog_templates
                SET current_version = ?, updated_at = ?
                WHERE id = ?
                """,
                (next_version, now, current.id),
            )
        return self.get_template(current.id)

    def update_metadata(
        self,
        template_ref: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> RuleCatalogTemplate:
        current = self.get_template(template_ref)
        next_name = current.name if name is None else str(name).strip()
        if not next_name:
            raise RuleCatalogError("Der Vorlagenname darf nicht leer sein.")
        next_status = current.status if status is None else _status(status)
        next_description = current.description if description is None else str(description).strip()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE rule_catalog_templates
                SET name = ?, description = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (next_name, next_description, next_status, _utc_now(), current.id),
            )
        return self.get_template(current.id)

    def get_template(self, template_ref: str, version: Optional[int] = None) -> RuleCatalogTemplate:
        normalized_key = _template_key(template_ref)
        with self._connect() as connection:
            template_row = connection.execute(
                """
                SELECT * FROM rule_catalog_templates
                WHERE id = ? OR template_key = ?
                """,
                (str(template_ref), normalized_key),
            ).fetchone()
            if not template_row:
                raise RuleTemplateNotFoundError(f"Regelvorlage nicht gefunden: {template_ref}")
            selected_version = int(version or template_row["current_version"])
            version_row = connection.execute(
                """
                SELECT * FROM rule_catalog_versions
                WHERE template_id = ? AND version = ?
                """,
                (template_row["id"], selected_version),
            ).fetchone()
        if not version_row:
            raise RuleTemplateNotFoundError(f"Version {selected_version} der Regelvorlage wurde nicht gefunden.")
        return self._template(template_row, version_row)

    def list_templates(self, status: Optional[str] = None) -> list[RuleCatalogTemplate]:
        params: tuple[Any, ...] = ()
        where = ""
        if status is not None:
            where = "WHERE status = ?"
            params = (_status(status),)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id
                FROM rule_catalog_templates
                {where}
                ORDER BY name COLLATE NOCASE, template_key
                """,
                params,
            ).fetchall()
        return [self.get_template(row["id"]) for row in rows]

    def bind_rule(
        self,
        *,
        template_ref: str,
        template_version: int,
        config_id: str,
        project: str,
        report_ref: str,
        group_ref: str,
        rule_ref: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> RuleTemplateBinding:
        template = self.get_template(template_ref, template_version)
        values = [config_id, project, report_ref, group_ref, rule_ref]
        if any(not str(value or "").strip() for value in values):
            raise RuleCatalogError("Eine Regelbindung benötigt Config, Projekt, Bericht, Regelgruppe und Regel.")
        now = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO rule_catalog_bindings (
                    template_id, template_version, config_id, project, report_ref,
                    group_ref, rule_ref, parameters_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(config_id, project, report_ref, group_ref, rule_ref) DO UPDATE SET
                    template_id = excluded.template_id,
                    template_version = excluded.template_version,
                    parameters_json = excluded.parameters_json,
                    updated_at = excluded.updated_at
                """,
                (
                    template.id,
                    template.version.version,
                    str(config_id).strip(),
                    str(project).strip(),
                    str(report_ref).strip(),
                    str(group_ref).strip(),
                    str(rule_ref).strip(),
                    _json(parameters or {}),
                    now,
                    now,
                ),
            )
            row = connection.execute(
                """
                SELECT * FROM rule_catalog_bindings
                WHERE config_id = ? AND project = ? AND report_ref = ?
                  AND group_ref = ? AND rule_ref = ?
                """,
                (config_id, project, report_ref, group_ref, rule_ref),
            ).fetchone()
        return self._binding(row)

    def list_bindings(
        self,
        *,
        template_ref: Optional[str] = None,
        config_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> list[RuleTemplateBinding]:
        clauses = []
        params: list[Any] = []
        if template_ref:
            template = self.get_template(template_ref)
            clauses.append("template_id = ?")
            params.append(template.id)
        if config_id:
            clauses.append("config_id = ?")
            params.append(config_id)
        if project:
            clauses.append("project = ?")
            params.append(project)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM rule_catalog_bindings {where} ORDER BY id",
                tuple(params),
            ).fetchall()
        return [self._binding(row) for row in rows]

    def set_candidate_decision(
        self,
        *,
        config_id: str,
        project: str,
        candidate_key: str,
        decision: Optional[str],
    ) -> None:
        values = [config_id, project, candidate_key]
        if any(not str(value or "").strip() for value in values):
            raise RuleCatalogError("Eine Kandidatenentscheidung benötigt Config, Projekt und Kandidatenschlüssel.")
        normalized = str(decision or "").strip().casefold()
        with self._connect() as connection:
            if not normalized:
                connection.execute(
                    """
                    DELETE FROM rule_catalog_candidate_decisions
                    WHERE config_id = ? AND project = ? AND candidate_key = ?
                    """,
                    (str(config_id).strip(), str(project).strip(), str(candidate_key).strip()),
                )
                return
            if normalized not in RULE_CANDIDATE_DECISIONS:
                raise RuleCatalogError(f"Unbekannte Kandidatenentscheidung: {decision}")
            connection.execute(
                """
                INSERT INTO rule_catalog_candidate_decisions (
                    config_id, project, candidate_key, decision, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(config_id, project, candidate_key) DO UPDATE SET
                    decision = excluded.decision,
                    updated_at = excluded.updated_at
                """,
                (
                    str(config_id).strip(),
                    str(project).strip(),
                    str(candidate_key).strip(),
                    normalized,
                    _utc_now(),
                ),
            )

    def list_candidate_decisions(self, *, config_id: str, project: str) -> Dict[str, str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT candidate_key, decision
                FROM rule_catalog_candidate_decisions
                WHERE config_id = ? AND project = ?
                """,
                (str(config_id).strip(), str(project).strip()),
            ).fetchall()
        return {row["candidate_key"]: row["decision"] for row in rows}

    def ensure_default_templates(self) -> None:
        defaults = [
            {
                "key": "required-field",
                "name": "Pflichtfeld / Leerprüfung",
                "description": "Prüft NULL und leere Zeichenketten.",
                "condition_template": "{field} IS NULL OR TRIM({field}) = ''",
                "message_de_template": "{displayName} ist leer",
                "message_en_template": "{displayName} is empty",
                "dimension": "Vollständigkeit",
                "rule_type": "completeness",
                "compatible_data_types": ["string"],
                "field_categories": ["master-data", "business-process"],
                "examples": [{"value": "", "deficient": True}, {"value": "Berlin", "deficient": False}],
            },
            {
                "key": "trim-whitespace",
                "name": "Führende oder folgende Leerzeichen",
                "description": "Erkennt Werte, die nicht ihrer getrimmten Form entsprechen.",
                "condition_template": "{field} <> TRIM({field})",
                "message_de_template": "{displayName} enthält äußere Leerzeichen",
                "message_en_template": "{displayName} contains surrounding whitespace",
                "dimension": "Einheitlichkeit",
                "rule_type": "trim_whitespace",
                "compatible_data_types": ["string"],
                "field_categories": ["master-data", "business-process"],
                "examples": [{"value": " Berlin ", "deficient": True}, {"value": "Berlin", "deficient": False}],
            },
            {
                "key": "minimum-length",
                "name": "Mindestlänge",
                "description": "Prüft die Mindestanzahl von Zeichen.",
                "condition_template": "LENGTH(TRIM({field})) < {min_length}",
                "message_de_template": "{displayName} ist kürzer als {min_length} Zeichen",
                "message_en_template": "{displayName} is shorter than {min_length} characters",
                "dimension": "Korrektheit",
                "rule_type": "min_length",
                "parameter_schema": {
                    "min_length": {"type": "integer", "required": True, "min": 1, "default": 2},
                },
                "compatible_data_types": ["string"],
                "field_categories": ["master-data", "business-process"],
                "examples": [{"value": "A", "deficient": True}, {"value": "AB", "deficient": False}],
            },
            {
                "key": "maximum-length",
                "name": "Maximallänge",
                "description": "Prüft die maximal erlaubte Anzahl von Zeichen.",
                "condition_template": "LENGTH(TRIM({field})) > {max_length}",
                "message_de_template": "{displayName} ist länger als {max_length} Zeichen",
                "message_en_template": "{displayName} is longer than {max_length} characters",
                "dimension": "Korrektheit",
                "rule_type": "max_length",
                "parameter_schema": {
                    "max_length": {"type": "integer", "required": True, "min": 1, "default": 100},
                },
                "compatible_data_types": ["string"],
                "field_categories": ["master-data", "business-process"],
                "examples": [{"value": "A" * 101, "deficient": True}, {"value": "AB", "deficient": False}],
            },
        ]
        for template in defaults:
            try:
                self.get_template(template["key"])
            except RuleTemplateNotFoundError:
                self.create_template(status="approved", **template)

    @staticmethod
    def _insert_version(
        connection: sqlite3.Connection,
        template_id: str,
        version: int,
        values: Dict[str, Any],
        created_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO rule_catalog_versions (
                template_id, version, condition_template, message_de_template,
                message_en_template, dimension, rule_type, parameter_schema_json,
                compatible_data_types_json, field_categories_json, examples_json,
                change_note, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                template_id,
                version,
                values["conditionTemplate"],
                values["messageDeTemplate"],
                values["messageEnTemplate"],
                values["dimension"],
                values["ruleType"],
                _json(values["parameterSchema"]),
                _json(values["compatibleDataTypes"]),
                _json(values["fieldCategories"]),
                _json(values["examples"]),
                values["changeNote"],
                created_at,
            ),
        )

    @classmethod
    def _template(cls, template_row: sqlite3.Row, version_row: sqlite3.Row) -> RuleCatalogTemplate:
        return RuleCatalogTemplate(
            id=template_row["id"],
            key=template_row["template_key"],
            name=template_row["name"],
            description=template_row["description"],
            status=template_row["status"],
            currentVersion=int(template_row["current_version"]),
            version=cls._version(version_row),
            createdAt=template_row["created_at"],
            updatedAt=template_row["updated_at"],
        )

    @staticmethod
    def _version(row: sqlite3.Row) -> RuleTemplateVersion:
        return RuleTemplateVersion(
            templateId=row["template_id"],
            version=int(row["version"]),
            conditionTemplate=row["condition_template"],
            messageDeTemplate=row["message_de_template"],
            messageEnTemplate=row["message_en_template"],
            dimension=row["dimension"],
            ruleType=row["rule_type"],
            parameterSchema=json.loads(row["parameter_schema_json"]),
            compatibleDataTypes=json.loads(row["compatible_data_types_json"]),
            fieldCategories=json.loads(row["field_categories_json"]),
            examples=json.loads(row["examples_json"]),
            changeNote=row["change_note"],
            createdAt=row["created_at"],
        )

    @staticmethod
    def _binding(row: sqlite3.Row) -> RuleTemplateBinding:
        return RuleTemplateBinding(
            id=int(row["id"]),
            templateId=row["template_id"],
            templateVersion=int(row["template_version"]),
            configId=row["config_id"],
            project=row["project"],
            reportRef=row["report_ref"],
            groupRef=row["group_ref"],
            ruleRef=row["rule_ref"],
            parameters=json.loads(row["parameters_json"]),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )


def _version_values(
    condition_template: str,
    message_de_template: str,
    message_en_template: str,
    dimension: str,
    rule_type: str,
    parameter_schema: Optional[Dict[str, Dict[str, Any]]],
    compatible_data_types: Optional[list[str]],
    field_categories: Optional[list[str]],
    examples: Optional[list[Dict[str, Any]]],
    change_note: str,
) -> Dict[str, Any]:
    schema = dict(parameter_schema or {})
    validate_rule_template(condition_template, message_de_template, message_en_template, schema)
    dimension = str(dimension or "").strip()
    rule_type = str(rule_type or "").strip()
    if not dimension or not rule_type:
        raise RuleCatalogError("DQ-Typ und Regeltyp dürfen nicht leer sein.")
    return {
        "conditionTemplate": str(condition_template).strip(),
        "messageDeTemplate": str(message_de_template or "").strip(),
        "messageEnTemplate": str(message_en_template or "").strip(),
        "dimension": dimension,
        "ruleType": rule_type,
        "parameterSchema": schema,
        "compatibleDataTypes": _string_list(compatible_data_types),
        "fieldCategories": _string_list(field_categories),
        "examples": list(examples or []),
        "changeNote": str(change_note or "").strip(),
    }


def _template_key(value: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().casefold()).strip("_")
    if not key:
        raise RuleCatalogError("Der Vorlagenschlüssel darf nicht leer sein.")
    return key


def _status(value: str) -> str:
    status = str(value or "").strip().casefold()
    if status not in RULE_TEMPLATE_STATUSES:
        raise RuleCatalogError(f"Ungültiger Vorlagenstatus: {value}")
    return status


def _string_list(values: Optional[list[str]]) -> list[str]:
    return list(dict.fromkeys(str(value).strip() for value in (values or []) if str(value).strip()))


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
