import argparse
import os
from pathlib import Path
from typing import Optional, Sequence

import uvicorn

from backend import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lokale NEMO-Deficiencies-Webanwendung starten")
    parser.add_argument("--host", default="127.0.0.1", help="Bind-Adresse (Standard: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (Standard: 8000)")
    parser.add_argument("--home", type=Path, help="Ordner für Datenbank, Schlüssel, Configs und Logs")
    parser.add_argument("--reload", action="store_true", help="Entwicklungsmodus mit automatischem Neuladen")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if args.home:
        os.environ["NEMO_DEFICIENCIES_HOME"] = str(args.home.expanduser().resolve())
    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
