import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional


@dataclass(frozen=True)
class EditorBaseline:
    id: str
    configId: str
    project: str
    reportRef: str
    reportId: str
    reportName: str
    originalSql: str
    editorModel: Dict[str, Any]
    createdAt: str

    def to_dict(self, include_model: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "configId": self.configId,
            "project": self.project,
            "reportRef": self.reportRef,
            "reportId": self.reportId,
            "reportName": self.reportName,
            "createdAt": self.createdAt,
        }
        if include_model:
            data["editorModel"] = self.editorModel
        return data


class EditorBaselineStore:
    """Stores the first imported report state and never overwrites it."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS editor_baselines (
                    id TEXT PRIMARY KEY,
                    config_id TEXT NOT NULL,
                    project TEXT NOT NULL,
                    report_ref TEXT NOT NULL,
                    report_id TEXT NOT NULL DEFAULT '',
                    report_name TEXT NOT NULL DEFAULT '',
                    original_sql TEXT NOT NULL,
                    editor_model_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(config_id, project, report_ref)
                )
                """
            )

    def capture_if_missing(
        self,
        config_id: str,
        project: str,
        report_ref: str,
        original_sql: str,
        editor_model: Dict[str, Any],
    ) -> EditorBaseline:
        baseline_id = baseline_key(config_id, project, report_ref)
        report = editor_model.get("report") or {}
        now = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO editor_baselines (
                    id, config_id, project, report_ref, report_id, report_name,
                    original_sql, editor_model_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    baseline_id,
                    config_id,
                    project,
                    report_ref,
                    str(report.get("id") or report_ref or ""),
                    str(report.get("displayName") or report.get("internalName") or report_ref or ""),
                    original_sql,
                    json.dumps(editor_model, ensure_ascii=False, sort_keys=True),
                    now,
                ),
            )
        baseline = self.get_baseline(config_id, project, report_ref)
        if baseline is None:
            raise RuntimeError("Ursprungsbericht konnte nicht gespeichert werden.")
        return baseline

    def get_baseline(self, config_id: str, project: str, report_ref: str) -> Optional[EditorBaseline]:
        baseline_id = baseline_key(config_id, project, report_ref)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM editor_baselines WHERE id = ?",
                (baseline_id,),
            ).fetchone()
        if not row:
            return None
        return EditorBaseline(
            id=row["id"],
            configId=row["config_id"],
            project=row["project"],
            reportRef=row["report_ref"],
            reportId=row["report_id"],
            reportName=row["report_name"],
            originalSql=row["original_sql"],
            editorModel=json.loads(row["editor_model_json"]),
            createdAt=row["created_at"],
        )

    def find_report_ref_by_internal_name(
        self,
        config_id: str,
        project: str,
        internal_name: str,
    ) -> Optional[str]:
        wanted = str(internal_name or "").strip().casefold()
        if not wanted:
            return None
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT report_ref, editor_model_json FROM editor_baselines
                WHERE config_id = ? AND project = ?
                ORDER BY created_at ASC
                """,
                (config_id, project),
            ).fetchall()
        for row in rows:
            try:
                model = json.loads(row["editor_model_json"])
            except (TypeError, json.JSONDecodeError):
                continue
            report = model.get("report") or {}
            if str(report.get("internalName") or "").strip().casefold() == wanted:
                return str(row["report_ref"])
        return None


def baseline_key(config_id: str, project: str, report_ref: str) -> str:
    raw = f"{config_id}\0{project}\0{report_ref}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
