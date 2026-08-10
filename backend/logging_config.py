import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(project_root: Path) -> Path:
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "nemo_deficiencies.log"
    resolved_log_file = log_file.resolve()

    root_logger = logging.getLogger()
    already_configured = any(
        getattr(handler, "nemo_deficiencies_handler", False)
        and Path(getattr(handler, "baseFilename", "")).resolve() == resolved_log_file
        for handler in root_logger.handlers
    )
    if not already_configured:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        handler.nemo_deficiencies_handler = True
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(handler)

    if root_logger.level == logging.NOTSET or root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    return log_file
