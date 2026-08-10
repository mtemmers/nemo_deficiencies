import configparser
import tempfile
import unittest
from pathlib import Path

from backend.services.config_store import (
    ConfigStore,
    build_nemo_config_content,
    config_profile_name,
    read_nemo_config_settings,
    update_nemo_config_content,
)


class ConfigStoreTest(unittest.TestCase):
    def test_import_encrypts_and_decrypts_ini_file(self) -> None:
        ini_content = "[nemo]\ntenant=TenantA\nurl=https://example.invalid\npassword=top-secret\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "config.ini").write_text(ini_content, encoding="utf-8")

            store = ConfigStore(root)
            profiles = store.import_ini_files()

            self.assertEqual(1, len(profiles))
            self.assertEqual("config", profiles[0].name)
            self.assertEqual("config.ini", profiles[0].sourceFile)
            self.assertEqual("TenantA", profiles[0].tenant)
            self.assertEqual(ini_content, store.decrypt_config(profiles[0].id))
            self.assertNotIn(b"top-secret", store.db_path.read_bytes())
            self.assertTrue(store.key_path.exists())

    def test_root_ini_is_ignored_and_existing_profile_id_is_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "legacy.ini").write_text("[nemo]\ntenant=Wrong\n", encoding="utf-8")
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "config.ini").write_text("[nemo]\ntenant=TenantA\n", encoding="utf-8")

            store = ConfigStore(root)
            existing = store.upsert_config(
                config_id="legacy-profile-id",
                name="config",
                ini_content="[nemo]\ntenant=TenantA\n",
                source="imported-ini",
                source_file="config.ini",
            )
            profiles = store.import_ini_files()

            self.assertEqual([existing.id], [profile.id for profile in profiles])
            self.assertEqual(1, len(store.list_profiles()))

    def test_temporary_config_file_is_removed_after_use(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = ConfigStore(root)
            profile = store.create_config("local", "[nemo]\nvalue=1\n")

            with store.temporary_config_file(profile.id) as config_path:
                self.assertTrue(config_path.exists())
                self.assertEqual("[nemo]\nvalue=1\n", config_path.read_text(encoding="utf-8"))

            self.assertFalse(config_path.exists())

    def test_credentials_config_is_encrypted_and_ini_safe(self) -> None:
        password = "secret%value#1"
        ini_content = build_nemo_config_content("Tenant A", "user@example.org", password)
        parser = configparser.ConfigParser()
        parser.read_string(ini_content)

        self.assertEqual("Tenant A", parser.get("nemo_library", "tenant"))
        self.assertEqual("user@example.org", parser.get("nemo_library", "userid"))
        self.assertEqual(password, parser.get("nemo_library", "password"))
        self.assertEqual("https://enter.nemo-ai.com", parser.get("nemo_library", "nemo_url"))
        self.assertEqual("prod", parser.get("nemo_library", "environment"))
        self.assertEqual("config_tenant_a", config_profile_name("Tenant A"))

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConfigStore(Path(temp_dir))
            profile = store.create_config(config_profile_name("Tenant A"), ini_content)

            self.assertEqual("Tenant A", profile.tenant)
            self.assertNotIn("password", profile.to_dict())
            self.assertNotIn(password.encode("utf-8"), store.db_path.read_bytes())

    def test_connection_settings_can_be_changed_without_losing_additional_values(self) -> None:
        original = build_nemo_config_content("nextgendemo", "old-user", "old%password")
        original += "metadata = C:/metadata.json\n"

        settings = read_nemo_config_settings(original)
        self.assertNotIn("password", settings)
        self.assertTrue(settings["hasPassword"])

        updated = update_nemo_config_content(
            original,
            tenant="nextgendemo",
            userid="new-user",
            password="",
            nemo_url="https://nextgendemo.enter.nemo-ai.com/",
            environment="nextgendemo",
        )
        parser = configparser.ConfigParser()
        parser.read_string(updated)
        self.assertEqual("old%password", parser.get("nemo_library", "password"))
        self.assertEqual("new-user", parser.get("nemo_library", "userid"))
        self.assertEqual("https://nextgendemo.enter.nemo-ai.com", parser.get("nemo_library", "nemo_url"))
        self.assertEqual("nextgendemo", parser.get("nemo_library", "environment"))
        self.assertEqual("C:/metadata.json", parser.get("nemo_library", "metadata"))

        changed_password = update_nemo_config_content(
            updated,
            tenant="nextgendemo",
            userid="new-user",
            password="replacement%password",
            nemo_url="https://nextgendemo.enter.nemo-ai.com",
            environment="nextgendemo",
        )
        parser.read_string(changed_password)
        self.assertEqual("replacement%password", parser.get("nemo_library", "password"))


if __name__ == "__main__":
    unittest.main()
