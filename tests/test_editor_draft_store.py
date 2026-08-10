import tempfile
import unittest
from pathlib import Path

from backend.services.editor_draft_store import EditorDraftStore


class EditorDraftStoreTest(unittest.TestCase):
    def test_save_get_update_and_delete_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EditorDraftStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")
            model = {
                "report": {"id": "report-1", "displayName": "Report 1"},
                "source": {"attributes": []},
                "checks": {"groups": []},
                "output": {"fields": []},
                "blocks": [],
                "summary": {},
                "validation": {"findings": []},
            }

            draft = store.save_draft(
                "cfg",
                "Master Data",
                "report-1",
                model,
                base_sql_hash="a" * 64,
            )
            loaded = store.get_draft("cfg", "Master Data", "report-1")

            self.assertIsNotNone(loaded)
            self.assertEqual(draft.id, loaded.id)
            self.assertEqual("report-1", loaded.reportId)
            self.assertEqual("Report 1", loaded.reportName)
            self.assertEqual("a" * 64, loaded.baseSqlHash)
            self.assertEqual(model, loaded.editorModel)

            updated_model = {
                **model,
                "report": {"id": "report-1", "displayName": "Report 1 Draft"},
            }
            updated = store.save_draft("cfg", "Master Data", "report-1", updated_model)

            self.assertEqual(draft.id, updated.id)
            self.assertEqual(draft.createdAt, updated.createdAt)
            self.assertEqual("Report 1 Draft", updated.reportName)
            self.assertEqual("a" * 64, updated.baseSqlHash)
            self.assertEqual(updated_model, updated.editorModel)
            self.assertTrue(store.delete_draft("cfg", "Master Data", "report-1"))
            self.assertIsNone(store.get_draft("cfg", "Master Data", "report-1"))
            self.assertFalse(store.delete_draft("cfg", "Master Data", "report-1"))


if __name__ == "__main__":
    unittest.main()
