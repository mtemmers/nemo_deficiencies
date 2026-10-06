import tempfile
import unittest
from pathlib import Path

from backend.services.ai_translation_cache_store import AITranslationCacheStore


class AITranslationCacheStoreTest(unittest.TestCase):
    def test_translation_survives_new_store_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "nemo_deficiencies.sqlite"
            store = AITranslationCacheStore(db_path)
            store.put("profile|provider|model", "de", "en", "Kundennummer fehlt", "Customer number is missing")

            reloaded = AITranslationCacheStore(db_path)

            self.assertEqual(
                "Customer number is missing",
                reloaded.get("profile|provider|model", "de", "en", "Kundennummer fehlt"),
            )
            self.assertIsNone(
                reloaded.get("profile|provider|other-model", "de", "en", "Kundennummer fehlt")
            )

    def test_cache_separates_translation_directions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AITranslationCacheStore(Path(temp_dir) / "cache.sqlite")
            store.put("profile", "de", "en", "Leer", "Empty")
            store.put("profile", "en", "de", "Empty", "Leer")

            self.assertEqual("Empty", store.get("profile", "de", "en", "Leer"))
            self.assertEqual("Leer", store.get("profile", "en", "de", "Empty"))


if __name__ == "__main__":
    unittest.main()
