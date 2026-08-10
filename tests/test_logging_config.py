import logging
import tempfile
import unittest
from pathlib import Path

from backend.logging_config import configure_logging


class LoggingConfigTest(unittest.TestCase):
    def test_configure_logging_creates_rotating_log_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            log_file = configure_logging(project_root)
            logging.getLogger("tests.logging").error("Testfehler für Logdatei")
            temporary_handlers = []
            for handler in logging.getLogger().handlers:
                if (
                    getattr(handler, "nemo_deficiencies_handler", False)
                    and Path(getattr(handler, "baseFilename", "")).resolve() == log_file.resolve()
                ):
                    handler.flush()
                    temporary_handlers.append(handler)

            self.assertEqual(project_root / "logs" / "nemo_deficiencies.log", log_file)
            self.assertTrue(log_file.exists())
            for handler in temporary_handlers:
                logging.getLogger().removeHandler(handler)
                handler.close()


if __name__ == "__main__":
    unittest.main()
