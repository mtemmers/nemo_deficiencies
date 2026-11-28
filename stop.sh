#!/usr/bin/env bash

PORT="${1:-8000}"
if [[ "$PORT" == "--port" || "$PORT" == "-p" ]]; then
  PORT="${2:-8000}"
fi

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Ungültiger Port: $PORT" >&2
  return 1 2>/dev/null || exit 1
fi

PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -z "$PIDS" ]]; then
  echo "Auf Port $PORT läuft keine Anwendung."
else
  echo "$PIDS" | xargs kill
  echo "NEMO Deficiencies auf Port $PORT wurde beendet."
fi

# Deaktiviert eine eventuell aktivierte venv, wenn das Skript mit `source ./stop.sh` aufgerufen wurde.
if [[ -n "${VIRTUAL_ENV:-}" ]] && command -v deactivate >/dev/null 2>&1; then
  deactivate
  echo "Virtuelle Umgebung deaktiviert."
fi

return 0 2>/dev/null || exit 0
