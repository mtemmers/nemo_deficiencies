import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from backend.services.editor_change_log_store import EditorChangeLogStore
from backend.services.editor_draft_store import EditorDraftStore


class EditorChangeLogStoreTest(unittest.TestCase):
    def test_invalidate_undoable_changes_preserves_audit_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EditorChangeLogStore(Path(temp_dir) / "data.sqlite")
            change = store.append_change(
                config_id="cfg",
                project="Master Data",
                report_ref="report-1",
                change_type="rule_message",
                target_path="checks.groups.0.rules.0.message",
                old_value="alt",
                new_value="neu",
            )

            invalidated = store.invalidate_undoable_changes("cfg", "Master Data", "report-1")
            persisted = store.get_change(change.id)

            self.assertEqual(1, invalidated)
            self.assertIsNotNone(persisted.undoneAt)
            self.assertFalse(persisted.to_dict()["undoable"])

    def test_append_list_and_undo_change_on_persisted_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            draft_store = EditorDraftStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            original_model = minimal_model("alte Meldung")
            changed_model = minimal_model("neue Meldung")

            draft_store.save_draft("cfg", "Master Data", "report-1", changed_model)
            change = change_store.append_change(
                config_id="cfg",
                project="Master Data",
                report_ref="report-1",
                change_type="rule_message",
                target_path="checks.groups.0.rules.0.message",
                target_label="NAME · Fehlermeldung",
                old_value="alte Meldung",
                new_value="neue Meldung",
            )

            self.assertEqual("neue Meldung", change.newValue)
            self.assertEqual(1, len(change_store.list_changes("cfg", "Master Data", "report-1")))

            undone_change, undone_model = change_store.undo_latest(draft_store, "cfg", "Master Data", "report-1")
            loaded_draft = draft_store.get_draft("cfg", "Master Data", "report-1")

            self.assertIsNotNone(undone_change.undoneAt)
            self.assertEqual("alte Meldung", undone_model["checks"]["groups"][0]["rules"][0]["message"])
            self.assertEqual("alte Meldung", loaded_draft.editorModel["checks"]["groups"][0]["rules"][0]["message"])

    def test_undo_restores_rule_list_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            draft_store = EditorDraftStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            original_model = minimal_model("erste Meldung")
            changed_model = minimal_model("erste Meldung")
            changed_model["checks"]["groups"][0]["rules"].append(
                {
                    "condition": "NAME = 'X'",
                    "message": "zweite Meldung",
                    "dimension": "Korrektheit",
                    "ruleType": "custom",
                    "active": True,
                }
            )

            draft_store.save_draft("cfg", "Master Data", "report-1", changed_model)
            change_store.append_change(
                config_id="cfg",
                project="Master Data",
                report_ref="report-1",
                change_type="rule_create",
                target_path="checks.groups.0.rules",
                target_label="NAME · Regel angelegt",
                old_value=original_model["checks"]["groups"][0]["rules"],
                new_value=changed_model["checks"]["groups"][0]["rules"],
            )

            _, undone_model = change_store.undo_latest(draft_store, "cfg", "Master Data", "report-1")

            self.assertEqual(1, len(undone_model["checks"]["groups"][0]["rules"]))
            self.assertEqual("erste Meldung", undone_model["checks"]["groups"][0]["rules"][0]["message"])

    def test_undo_restores_complete_model_after_original_restore(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            draft_store = EditorDraftStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            original_model = minimal_model("Ursprung")
            changed_model = minimal_model("Bearbeitet")

            draft_store.save_draft("cfg", "Master Data", "report-1", original_model)
            change_store.append_change(
                config_id="cfg",
                project="Master Data",
                report_ref="report-1",
                change_type="restore_original",
                target_path="$",
                target_label="Ursprungsbericht wiederhergestellt",
                old_value=changed_model,
                new_value=original_model,
            )

            _, undone_model = change_store.undo_latest(draft_store, "cfg", "Master Data", "report-1")

            self.assertEqual("Bearbeitet", undone_model["checks"]["groups"][0]["rules"][0]["message"])

    def test_undo_restores_deleted_rule_group(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            draft_store = EditorDraftStore(db_path)
            change_store = EditorChangeLogStore(db_path)
            original_model = minimal_model("Name fehlt")
            second_group = deepcopy(original_model["checks"]["groups"][0])
            second_group.update({"number": 2, "title": "CITY", "field": "CITY", "description": "Ort"})
            second_group["rules"][0].update({"condition": "CITY IS NULL", "message": "Ort fehlt"})
            original_model["checks"]["groups"].append(second_group)
            changed_model = deepcopy(original_model)
            changed_model["checks"]["groups"].pop(0)

            draft_store.save_draft("cfg", "Master Data", "report-1", changed_model)
            change_store.append_change(
                config_id="cfg",
                project="Master Data",
                report_ref="report-1",
                change_type="group_delete",
                target_path="checks.groups",
                target_label="NAME · Regelgruppe entfernt",
                old_value=original_model["checks"]["groups"],
                new_value=changed_model["checks"]["groups"],
            )

            _, undone_model = change_store.undo_latest(draft_store, "cfg", "Master Data", "report-1")

            self.assertEqual(2, len(undone_model["checks"]["groups"]))
            self.assertEqual("NAME", undone_model["checks"]["groups"][0]["field"])


def minimal_model(message: str) -> dict:
    return {
        "report": {"id": "report-1", "displayName": "Report 1"},
        "source": {"attributes": []},
        "checks": {
            "groups": [
                {
                    "number": 1,
                    "title": "NAME",
                    "field": "NAME",
                    "description": "Name",
                    "rules": [
                        {
                            "condition": "NAME IS NULL",
                            "message": message,
                            "dimension": "Vollständigkeit",
                            "ruleType": "custom",
                            "active": True,
                        }
                    ],
                }
            ]
        },
        "output": {"fields": []},
        "blocks": [],
        "summary": {},
        "validation": {"findings": []},
    }


if __name__ == "__main__":
    unittest.main()
