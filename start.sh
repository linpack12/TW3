#!/bin/bash
set -euo pipefail

MODE="${1:-}"

# --- Helpers ---------------------------------------------------------------

wait_for_mcp() {
  # Vänta tills FastAPI/MCP-servern svarar på /health (port 8000).
  python - <<'PY'
import time, sys, requests
url = "http://127.0.0.1:8000/health"
deadline = time.time() + 20.0  # ~20s timeout
while time.time() < deadline:
    try:
        r = requests.get(url, timeout=0.5)
        if r.status_code == 200:
            sys.exit(0)
    except Exception:
        pass
    time.sleep(0.2)
print("ERROR: MCP server healthcheck failed (/health)", file=sys.stderr)
sys.exit(1)
PY
}

wait_for_http8888() {
  # Vänta tills den lokala HTTP-servern lyssnar (port 8888).
  python - <<'PY'
import time, sys, requests
url = "http://127.0.0.1:8888/"
deadline = time.time() + 10.0  # ~10s timeout räcker för SimpleHTTPServer
while time.time() < deadline:
    try:
        r = requests.get(url, timeout=0.5)
        # 200/404 båda duger: vi vill bara se att servern lyssnar
        if r.status_code in (200, 404):
            sys.exit(0)
    except Exception:
        pass
    time.sleep(0.2)
print("ERROR: Local HTTP server on :8888 did not become ready", file=sys.stderr)
sys.exit(1)
PY
}

graceful_kill() {
  # Döda PIDs om de finns
  for pid in "$@"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
      # Vänta kort på stängning
      for _ in {1..20}; do
        if kill -0 "${pid}" 2>/dev/null; then
          sleep 0.1
        else
          break
        fi
      done
      # Hårddöd som sista utväg
      kill -9 "${pid}" 2>/dev/null || true
    fi
  done
}

# --- Modes -----------------------------------------------------------------

if [[ "$MODE" = "demo:part1" ]]; then
  echo "[boot] running part 1 demo flow"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
  SERVER_PID=$!

  # Vänta tills MCP-servern verkligen är uppe
  wait_for_mcp

  python /app/demo.py

  graceful_kill "$SERVER_PID"

elif [[ "$MODE" = "demo:part2" ]]; then
  echo "[boot] running part 2 demo flow"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
  SERVER_PID=$!

  # Vänta tills MCP-servern verkligen är uppe
  wait_for_mcp

  python /app/run_local_server.py &
  HTTP_PID=$!

  # Vänta tills lokala http-servern lyssnar
  wait_for_http8888

  python /app/demo_part_2.py

  graceful_kill "$HTTP_PID" "$SERVER_PID"

elif [[ "$MODE" = "demo:all" ]]; then
  echo "[boot] running complete demo flow (part 1 + part 2)"

  # --- Part 1 ---
  echo "[boot] starting part 1 demo"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
  SERVER_PID=$!

  wait_for_mcp

  python /app/demo.py

  graceful_kill "$SERVER_PID"

  echo "[boot] part 1 demo completed"

  # --- Part 2 ---
  echo "[boot] starting part 2 demo"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
  SERVER_PID=$!

  wait_for_mcp

  python /app/run_local_server.py &
  HTTP_PID=$!

  wait_for_http8888

  python /app/demo_part_2.py

  graceful_kill "$HTTP_PID" "$SERVER_PID"

  echo "[boot] part 2 demo completed"

elif [[ "$MODE" = "server" ]]; then
  echo "[boot] running server mode - mcp server only"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000

elif [[ "$MODE" = "server:http" ]]; then
  echo "[boot] running server mode - mcp server + http server"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
  SERVER_PID=$!

  wait_for_mcp

  python /app/run_local_server.py &
  HTTP_PID=$!

  wait_for_http8888

  echo "[boot] both servers running"
  trap 'graceful_kill "$SERVER_PID" "$HTTP_PID"' EXIT
  # Håll processen vid liv tills någon stänger containern
  wait

else
  echo "[boot] running server mode (default)"
  uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000
fi
