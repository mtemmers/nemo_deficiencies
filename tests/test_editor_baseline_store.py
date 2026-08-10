import tempfile
import unittest
from pathlib import Path

from backend.services.editor_baseline_store import EditorBaselineStore


class EditorBaselineStoreTest(unittest.TestCase):
    def test_first_import_is_persisted_and_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EditorBaselineStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")
            original = minimal_model("Ursprung")
            changed = minimal_model("Späterer Stand")

            first = store.capture_if_missing("cfg", "Master Data", "report-1", "SELECT 'original'", original)
            second = store.capture_if_missing("cfg", "Master Data", "report-1", "SELECT 'changed'", changed)

            self.assertEqual(first.id, second.id)
            self.assertEqual(first.createdAt, second.createdAt)
            self.assertEqual("SELECT 'original'", second.originalSql)
            self.assertEqual("Ursprung", second.editorModel["checks"]["groups"][0]["rules"][0]["message"])

    def test_existing_guid_reference_is_found_by_internal_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EditorBaselineStore(Path(temp_dir) / "data" / "nemo_deficiencies.sqlite")
            model = minimal_model("Ursprung")
            model["report"]["internalName"] = "deficiencies_parts"
            store.capture_if_missing("cfg", "Master Data", "old-guid", "SELECT 1", model)

            report_ref = store.find_report_ref_by_internal_name("cfg", "Master Data", "DEFICIENCIES_PARTS")

            self.assertEqual("old-guid", report_ref)


def minimal_model(message: str) -> dict:
    return {
        "report": {"id": "report-1", "displayName": "Report 1"},
        "source": {"attributes": []},
        "checks": {"groups": [{"rules": [{"message": message}]}]},
        "output": {"fields": []},
        "blocks": [],
        "summary": {},
        "validation": {"findings": []},
    }


if __name__ == "__main__":
    unittest.main()
