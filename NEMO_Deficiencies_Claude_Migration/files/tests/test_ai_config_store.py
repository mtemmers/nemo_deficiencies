import tempfile
import unittest
from pathlib import Path

from backend.services.ai_config_store import AIConfigStore


class AIConfigStoreTest(unittest.TestCase):
    def test_api_key_is_encrypted_and_not_exposed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AIConfigStore(Path(temp_dir))
            profile = store.create_profile("Groq", "gsk-secret")

            public_data = profile.to_dict()
            settings = store.resolve_settings(profile.id)
            database_bytes = store.db_path.read_bytes()

            self.assertTrue(public_data["apiKeyConfigured"])
            self.assertNotIn("apiKey", public_data)
            self.assertNotIn("nemoConfigId", public_data)
            self.assertEqual("gsk-secret", settings.api_key)
            self.assertNotIn(b"gsk-secret", database_bytes)

    def test_profile_is_available_as_global_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AIConfigStore(Path(temp_dir))
            profile = store.create_profile("Groq", "gsk-secret")

            self.assertEqual(profile.id, store.list_profiles()[0].id)
            self.assertEqual("gsk-secret", store.resolve_settings().api_key)

    def test_local_openai_compatible_profile_does_not_require_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AIConfigStore(Path(temp_dir))
            profile = store.create_profile(
                "Ollama lokal",
                "",
                provider="ollama",
                base_url="http://localhost:11434/v1",
                model="qwen3:8b",
            )

            settings = store.resolve_settings(profile.id)

            self.assertEqual("ollama", settings.provider)
            self.assertEqual("", settings.api_key)
            self.assertFalse(profile.apiKeyConfigured)

    def test_same_profile_name_can_be_updated_to_another_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AIConfigStore(Path(temp_dir))
            first = store.create_profile("Standard-KI", "gsk-secret")
            updated = store.create_profile(
                "Standard-KI",
                "",
                provider="lmstudio",
                base_url="http://localhost:1234/v1",
                model="local-model",
            )

            self.assertEqual(first.id, updated.id)
            self.assertEqual("lmstudio", updated.provider)


if __name__ == "__main__":
    unittest.main()
