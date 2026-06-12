#!/usr/bin/env bash
# Lokale Entwicklung ohne Docker (Linux / macOS)
set -e

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r backend/requirements.txt
fi

export MQTT_HOST=localhost
export MQTT_PORT=1883
export DB_PATH=".gardenflow/garden.db"

.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
