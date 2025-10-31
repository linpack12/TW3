#!/bin/bash
set -e

MODE="$1"

if [ "$MODE" = "demo" ]; then
    echo "[boot] running demo flow"
    uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!

    sleep 1

    python /app/demo.py

    kill $SERVER_PID
else
    echo "[boot] running server mode"
    uvicorn src.mcp_server.app:app --host 0.0.0.0 --port 8000
fi
