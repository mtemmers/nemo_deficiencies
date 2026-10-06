import tomllib
import unittest
from pathlib import Path

from backend import __version__
from backend.cli import build_parser
from backend.main import FRONTEND_DIR, app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PackageMetadataTest(unittest.TestCase):
    def test_windows_autostart_scripts_are_available(self) -> None:
        install_script = (PROJECT_ROOT / "install-autostart.ps1").read_text(encoding="utf-8")
        uninstall_script = (PROJECT_ROOT / "uninstall-autostart.ps1").read_text(encoding="utf-8")

        self.assertIn("Register-ScheduledTask", install_script)
        self.assertIn("New-ScheduledTaskTrigger -AtLogOn", install_script)
        self.assertIn("start.ps1", install_script)
        self.assertIn("Unregister-ScheduledTask", uninstall_script)

    def test_version_and_console_command_are_consistent(self) -> None:
        metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertRegex(__version__, r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
        self.assertEqual(__version__, app.version)
        self.assertEqual("backend.cli:main", metadata["project"]["scripts"]["nemo-deficiencies"])
        self.assertEqual("backend.__version__", metadata["tool"]["setuptools"]["dynamic"]["version"]["attr"])

    def test_windows_installer_and_release_workflow_are_available(self) -> None:
        self.assertTrue((PROJECT_ROOT / "backend" / "desktop.py").exists())
        self.assertTrue((PROJECT_ROOT / "nemo_deficiencies.spec").exists())
        self.assertTrue((PROJECT_ROOT / "installer" / "nemo_deficiencies.iss").exists())
        self.assertTrue((PROJECT_ROOT / "scripts" / "build-installer.ps1").exists())
        self.assertTrue((PROJECT_ROOT / "scripts" / "publish-release.ps1").exists())
        self.assertTrue((PROJECT_ROOT / ".github" / "workflows" / "release.yml").exists())

    def test_frontend_is_part_of_backend_package(self) -> None:
        self.assertEqual(PROJECT_ROOT / "backend" / "frontend", FRONTEND_DIR)
        self.assertTrue((FRONTEND_DIR / "index.html").exists())
        self.assertTrue((FRONTEND_DIR / "app.js").exists())
        self.assertTrue((FRONTEND_DIR / "styles.css").exists())

    def test_cli_defaults_to_local_port_8000(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual("127.0.0.1", args.host)
        self.assertEqual(8000, args.port)
        self.assertFalse(args.reload)


if __name__ == "__main__":
    unittest.main()
