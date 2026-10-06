"""Desktop launcher for the packaged Windows application."""

import json
import ctypes
import os
import socket
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8000
APP_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{APP_URL}/api/health"


def _bootstrap_log(message: str) -> None:
    local_app_data = os.getenv("LOCALAPPDATA")
    app_home = Path(local_app_data) / "NEMO Deficiencies" if local_app_data else Path.home() / ".nemo_deficiencies"
    log_file = app_home / "logs" / "desktop-startup.log"
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as stream:
            stream.write(f"{datetime.now().isoformat(timespec='seconds')} {message}\n")
    except OSError:
        pass


def _show_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, message, "NEMO Deficiencies", 0x10)


def _port_is_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.4)
        return connection.connect_ex((HOST, PORT)) == 0


def _application_is_running() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and payload.get("status") == "ok"
    except (OSError, ValueError, urllib.error.URLError):
        return False


def _open_browser_when_ready() -> None:
    for _attempt in range(60):
        if _application_is_running():
            webbrowser.open(APP_URL)
            return
        time.sleep(0.25)


def main() -> None:
    _bootstrap_log("Desktop-Start angefordert.")
    if _port_is_open():
        if _application_is_running():
            _bootstrap_log("Bereits laufende Anwendung erkannt; Browser wird geöffnet.")
            webbrowser.open(APP_URL)
            return
        _bootstrap_log(f"Start abgebrochen: Port {PORT} ist durch eine andere Anwendung belegt.")
        _show_error(
            f"Port {PORT} wird bereits von einer anderen Anwendung verwendet. "
            "Bitte diese Anwendung beenden und NEMO Deficiencies erneut starten."
        )
        return

    try:
        _bootstrap_log("Lade Webanwendung.")
        import uvicorn

        from backend.main import app

        _bootstrap_log("Webanwendung geladen; Server wird gestartet.")
        threading.Thread(target=_open_browser_when_ready, daemon=True).start()
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_config=None,
            access_log=False,
        )
    except Exception as exc:
        _bootstrap_log(f"Start fehlgeschlagen: {type(exc).__name__}: {exc}")
        _show_error(
            "NEMO Deficiencies konnte nicht gestartet werden. "
            "Details stehen unter AppData\\Local\\NEMO Deficiencies\\logs\\desktop-startup.log."
        )
        raise


if __name__ == "__main__":
    main()
