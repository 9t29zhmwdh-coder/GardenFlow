# Lokale Entwicklung ohne Docker (Windows PowerShell)
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r backend\requirements.txt
}

$env:MQTT_HOST = "localhost"
$env:MQTT_PORT = "1883"
$env:DB_PATH   = ".gardenflow\garden.db"

.\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
