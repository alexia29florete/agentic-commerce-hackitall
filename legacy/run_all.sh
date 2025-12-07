#!/usr/bin/env bash
set -e

echo "Starting Flask backend..."
export FLASK_APP=server.py
export FLASK_ENV=development

flask run --host=127.0.0.1 --port=5000 &
BACKEND_PID=$!

sleep 2

echo "Opening browser..."
xdg-open http://127.0.0.1:5000 || true

wait $BACKEND_PID
