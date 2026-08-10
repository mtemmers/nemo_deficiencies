import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional


@dataclass(frozen=True)
class EditorDraft:
    id: str
    configId: str
    project: str
    reportRef: str
    reportId: str
    reportName: str
    baseSqlHash: str
    editorModel: Dict[str, Any]
    createdAt: str
    updatedAt: str

    def to_dict(self, include_model: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "configId": self.configId,
            "project": self.project,
            "reportRef": self.reportRef,
            "reportId": self.reportId,
            "reportName": self.reportName,
            "baseSqlHash": self.baseSqlHash,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
        if include_model:
            data["editorModel"] = self.editorModel
        return data


class EditorDraftStore:
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
                CREATE TABLE IF NOT EXISTS editor_drafts (
                    id TEXT PRIMARY KEY,
                    config_id TEXT NOT NULL,
                    project TEXT NOT NULL,
                    report_ref TEXT NOT NULL,
                    report_id TEXT NOT NULL DEFAULT '',
                    report_name TEXT NOT NULL DEFAULT '',
                    base_sql_hash TEXT NOT NULL DEFAULT '',
                    editor_model_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(config_id, project, report_ref)
                )
                """
            )
            columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(editor_drafts)").fetchall()
            }
            if "base_sql_hash" not in columns:
                connection.execute(
                    "ALTER TABLE editor_drafts ADD COLUMN base_sql_hash TEXT NOT NULL DEFAULT ''"
                )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_editor_drafts_lookup
                ON editor_drafts(config_id, project, report_ref)
                """
            )

    def save_draft(
        self,
        config_id: str,
        project: str,
        report_ref: str,
        editor_model: Dict[str, Any],
        base_sql_hash: str = "",
    ) -> EditorDraft:
        draft_id = draft_key(config_id, project, report_ref)
        now = _utc_now()
        report = editor_model.get("report") or {}
        report_id = str(report.get("id") or report_ref or "")
        report_name = str(report.get("displayName") or report.get("internalName") or report_ref or "")
        model_json = json.dumps(editor_model, ensure_ascii=False, sort_keys=True)

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM editor_drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """
                INSERT INTO editor_drafts (
                    id, config_id, project, report_ref, report_id, report_name,
                    base_sql_hash, editor_model_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    editor_model_json = excluded.editor_model_json,
                    report_id = excluded.report_id,
                    report_name = excluded.report_name,
                    base_sql_hash = CASE
                        WHEN excluded.base_sql_hash <> '' THEN excluded.base_sql_hash
                        ELSE editor_drafts.base_sql_hash
                    END,
                    updated_at = excluded.updated_at
                """,
                (
                    draft_id,
                    config_id,
                    project,
                    report_ref,
                    report_id,
                    report_name,
                    str(base_sql_hash or ""),
                    model_json,
                    created_at,
                    now,
                ),
            )
        draft = self.get_draft(config_id, project, report_ref)
        if draft is None:
            raise RuntimeError("Draft konnte nicht gespeichert werden.")
        return draft

    def get_draft(self, config_id: str, project: str, report_ref: str) -> Optional[EditorDraft]:
        draft_id = draft_key(config_id, project, report_ref)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM editor_drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()
        return self._draft_from_row(row) if row else None

    def delete_draft(self, config_id: str, project: str, report_ref: str) -> bool:
        draft_id = draft_key(config_id, project, report_ref)
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM editor_drafts WHERE id = ?", (draft_id,))
        return cursor.rowcount > 0

    @staticmethod
    def _draft_from_row(row: sqlite3.Row) -> EditorDraft:
        return EditorDraft(
            id=row["id"],
            configId=row["config_id"],
            project=row["project"],
            reportRef=row["report_ref"],
            reportId=row["report_id"],
            reportName=row["report_name"],
            baseSqlHash=row["base_sql_hash"],
            editorModel=json.loads(row["editor_model_json"]),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )


def draft_key(config_id: str, project: str, report_ref: str) -> str:
    raw = f"{config_id}\0{project}\0{report_ref}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
