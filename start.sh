#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"
if [[ "$PORT" == "--port" || "$PORT" == "-p" ]]; then
  PORT="${2:-8000}"
fi

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Ungültiger Port: $PORT" >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

find_python() {
  local candidates=("$VENV_PYTHON")
  if [[ -n "${CONDA_PREFIX:-}" ]]; then
    candidates+=("$CONDA_PREFIX/bin/python")
  fi
  candidates+=("$HOME/.conda/envs/nemo_import_export/bin/python")
  if command -v python3 >/dev/null 2>&1; then
    candidates+=("$(command -v python3)")
  fi
  if command -v python >/dev/null 2>&1; then
    candidates+=("$(command -v python)")
  fi

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]] && "$candidate" -c "import fastapi, uvicorn, nemo_library" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

create_venv() {
  echo "Keine passende Python-Umgebung gefunden. Richte .venv ein..."
  if command -v uv >/dev/null 2>&1; then
    if [[ ! -x "$VENV_PYTHON" ]]; then
      uv venv --python 3.12 "$VENV_DIR"
    fi
    uv pip install --python "$VENV_PYTHON" -e "$PROJECT_ROOT"
    if uv pip list --python "$VENV_PYTHON" 2>/dev/null | grep -qi "^hubspot " && \
       uv pip list --python "$VENV_PYTHON" 2>/dev/null | grep -qi "^hubspot-api-client "; then
      uv pip uninstall --python "$VENV_PYTHON" hubspot
      uv pip install --python "$VENV_PYTHON" --reinstall --no-deps hubspot-api-client
    fi
    return 0
  fi

  local base_python=""
  local py_cmd
  for py_cmd in python3.12 python3.11 python3; do
    if command -v "$py_cmd" >/dev/null 2>&1; then
      if "$py_cmd" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >/dev/null 2>&1; then
        base_python="$(command -v "$py_cmd")"
        break
      fi
    fi
  done

  if [[ -z "$base_python" ]]; then
    echo "Fehler: Python >= 3.11 oder uv wird zum Erstellen von .venv benötigt." >&2
    exit 1
  fi

  if [[ ! -x "$VENV_PYTHON" ]]; then
    "$base_python" -m venv "$VENV_DIR"
  fi
  "$VENV_PYTHON" -m pip install --upgrade pip
  "$VENV_PYTHON" -m pip install -e "$PROJECT_ROOT"
  if "$VENV_PYTHON" -m pip show hubspot >/dev/null 2>&1 && \
     "$VENV_PYTHON" -m pip show hubspot-api-client >/dev/null 2>&1; then
    "$VENV_PYTHON" -m pip uninstall -y hubspot
    "$VENV_PYTHON" -m pip install --force-reinstall --no-deps hubspot-api-client
  fi
}

PYTHON_BIN="$(find_python || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  create_venv
  PYTHON_BIN="$(find_python || true)"
fi

if [[ -z "$PYTHON_BIN" ]]; then
  echo "NEMO Deficiencies konnte nach dem Einrichten von .venv nicht geladen werden:" >&2
  "$VENV_PYTHON" -c "import fastapi, uvicorn, nemo_library" || true
  exit 1
fi

is_port_listening() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

if is_port_listening "$PORT"; then
  echo "NEMO Deficiencies läuft bereits unter http://127.0.0.1:$PORT"
  exit 0
fi

LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
STDOUT_LOG="$LOG_DIR/server-output.log"
STDERR_LOG="$LOG_DIR/server-error.log"

cd "$PROJECT_ROOT"
nohup "$PYTHON_BIN" -m backend.cli --port "$PORT" >"$STDOUT_LOG" 2>"$STDERR_LOG" </dev/null &
SERVER_PID=$!

started=false
for _ in {1..30}; do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    break
  fi
  if is_port_listening "$PORT"; then
    started=true
    break
  fi
  sleep 0.5
done

if [[ "$started" != "true" ]]; then
  echo "NEMO Deficiencies konnte nicht gestartet werden (Prozess $SERVER_PID)." >&2
  if [[ -f "$STDERR_LOG" ]]; then
    tail -n 10 "$STDERR_LOG" >&2
  else
    echo "Kein Fehlerlog vorhanden." >&2
  fi
  exit 1
fi

echo "NEMO Deficiencies läuft unter http://127.0.0.1:$PORT"
echo "Python: $PYTHON_BIN"
echo "PID: $SERVER_PID"
