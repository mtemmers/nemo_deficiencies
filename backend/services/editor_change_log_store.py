import json
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from backend.services.editor_draft_store import EditorDraftStore
from backend.services.sql_model import normalize_editor_model


class EditorChangeNotFoundError(LookupError):
    pass


class EditorUndoError(ValueError):
    pass


@dataclass(frozen=True)
class EditorChange:
    id: int
    configId: str
    project: str
    reportRef: str
    changeType: str
    targetPath: str
    targetLabel: str
    oldValue: Any
    newValue: Any
    createdAt: str
    undoneAt: Optional[str]
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "configId": self.configId,
            "project": self.project,
            "reportRef": self.reportRef,
            "changeType": self.changeType,
            "targetPath": self.targetPath,
            "targetLabel": self.targetLabel,
            "oldValue": self.oldValue,
            "newValue": self.newValue,
            "createdAt": self.createdAt,
            "undoneAt": self.undoneAt,
            "note": self.note,
            "undoable": self.undoneAt is None,
        }


class EditorChangeLogStore:
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
                CREATE TABLE IF NOT EXISTS editor_change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_id TEXT NOT NULL,
                    project TEXT NOT NULL,
                    report_ref TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    target_path TEXT NOT NULL,
                    target_label TEXT NOT NULL DEFAULT '',
                    old_value_json TEXT NOT NULL,
                    new_value_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    undone_at TEXT,
                    note TEXT NOT NULL DEFAULT ''
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_editor_change_log_lookup
                ON editor_change_log(config_id, project, report_ref, id DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_editor_change_log_undo
                ON editor_change_log(config_id, project, report_ref, undone_at, id DESC)
                """
            )

    def append_change(
        self,
        config_id: str,
        project: str,
        report_ref: str,
        change_type: str,
        target_path: str,
        old_value: Any,
        new_value: Any,
        target_label: str = "",
        note: str = "",
    ) -> EditorChange:
        now = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO editor_change_log (
                    config_id, project, report_ref, change_type, target_path, target_label,
                    old_value_json, new_value_json, created_at, note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    config_id,
                    project,
                    report_ref,
                    change_type,
                    target_path,
                    target_label,
                    _json_value(old_value),
                    _json_value(new_value),
                    now,
                    note,
                ),
            )
            change_id = int(cursor.lastrowid)
        change = self.get_change(change_id)
        if change is None:
            raise RuntimeError("Änderung konnte nicht gespeichert werden.")
        return change

    def list_changes(self, config_id: str, project: str, report_ref: str, limit: int = 50) -> list[EditorChange]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM editor_change_log
                WHERE config_id = ? AND project = ? AND report_ref = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (config_id, project, report_ref, limit),
            ).fetchall()
        return [self._change_from_row(row) for row in rows]

    def get_change(self, change_id: int) -> Optional[EditorChange]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM editor_change_log WHERE id = ?", (change_id,)).fetchone()
        return self._change_from_row(row) if row else None

    def latest_undoable_change(self, config_id: str, project: str, report_ref: str) -> EditorChange:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM editor_change_log
                WHERE config_id = ? AND project = ? AND report_ref = ? AND undone_at IS NULL
                ORDER BY id DESC
                LIMIT 1
                """,
                (config_id, project, report_ref),
            ).fetchone()
        if not row:
            raise EditorChangeNotFoundError("Keine Änderung zum Rückgängigmachen vorhanden.")
        return self._change_from_row(row)

    def undo_latest(
        self,
        draft_store: EditorDraftStore,
        config_id: str,
        project: str,
        report_ref: str,
    ) -> tuple[EditorChange, Dict[str, Any]]:
        change = self.latest_undoable_change(config_id, project, report_ref)
        draft = draft_store.get_draft(config_id, project, report_ref)
        if draft is None:
            raise EditorUndoError("Kein Draft vorhanden, der rückgängig gemacht werden kann.")

        model = deepcopy(draft.editorModel)
        set_model_value(model, change.targetPath, change.oldValue)
        normalized_model = normalize_editor_model(model)
        draft_store.save_draft(config_id, project, report_ref, normalized_model)
        self.mark_undone(change.id)
        undone_change = self.get_change(change.id)
        return undone_change or change, normalized_model

    def mark_undone(self, change_id: int) -> None:
        now = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE editor_change_log SET undone_at = ? WHERE id = ? AND undone_at IS NULL",
                (now, change_id),
            )
        if cursor.rowcount == 0:
            raise EditorChangeNotFoundError("Änderung wurde nicht gefunden oder ist bereits rückgängig gemacht.")

    def invalidate_undoable_changes(self, config_id: str, project: str, report_ref: str) -> int:
        now = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE editor_change_log
                SET undone_at = ?
                WHERE config_id = ? AND project = ? AND report_ref = ? AND undone_at IS NULL
                """,
                (now, config_id, project, report_ref),
            )
        return cursor.rowcount

    @staticmethod
    def _change_from_row(row: sqlite3.Row) -> EditorChange:
        return EditorChange(
            id=int(row["id"]),
            configId=row["config_id"],
            project=row["project"],
            reportRef=row["report_ref"],
            changeType=row["change_type"],
            targetPath=row["target_path"],
            targetLabel=row["target_label"],
            oldValue=json.loads(row["old_value_json"]),
            newValue=json.loads(row["new_value_json"]),
            createdAt=row["created_at"],
            undoneAt=row["undone_at"],
            note=row["note"],
        )


def set_model_value(model: Dict[str, Any], target_path: str, value: Any) -> None:
    if target_path == "$":
        if not isinstance(value, dict):
            raise EditorUndoError("Der Ursprungsstand ist kein gültiges Editor-Modell.")
        model.clear()
        model.update(deepcopy(value))
        return
    tokens = parse_target_path(target_path)
    if not tokens:
        raise EditorUndoError("Leerer Zielpfad.")
    current: Any = model
    for token in tokens[:-1]:
        current = current[token]
    current[tokens[-1]] = value


def parse_target_path(target_path: str) -> list[Any]:
    tokens: list[Any] = []
    for raw_token in target_path.split("."):
        if raw_token == "":
            continue
        tokens.append(int(raw_token) if raw_token.isdigit() else raw_token)
    return tokens


def _json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
