<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>

  <h1>GardenFlow</h1>
</div>

[English](README.md)

# GardenFlow

[![CI](https://github.com/9t29zhmwdh-coder/GardenFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/9t29zhmwdh-coder/GardenFlow/actions) ![Platform](https://img.shields.io/badge/Platform-Linux_%7C_macOS-lightgrey) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![AI | Claude Code](https://img.shields.io/badge/AI-Claude_Code-black?logo=anthropic&logoColor=white) ![AI | Copilot](https://img.shields.io/badge/AI-Copilot-black?logo=github&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

Ein modulares Home-Garden-Automation-Toolkit; Sensoren (ESP32, Zigbee, MQTT) anschliessen, Automatisierungsregeln definieren und alles in einem Echtzeit-Web-Dashboard visualisieren.

Läuft auf **Linux, Windows und macOS** via Docker.

---

## Features

- **MQTT-Integration**: verbindet sich mit beliebigen MQTT-Brokern; erkennt Sensor-Topics automatisch unter `garden/sensors/{zone}/{type}`
- **Logik-Engine**: regelbasierte Automatisierung mit AND/OR-Bedingungen, konfigurierbarem Cooldown, Aktionen: Pumpe aktivieren, Alarm senden
- **Echtzeit-Dashboard**: Chart.js Live-Charts, manuelle Pumpensteuerung, Regelverwaltung; kein Build-Schritt, kein Framework
- **REST-API**: saubere Endpoints, automatisch generierte Swagger-UI unter `/docs`
- **WebSocket-Stream**: Sensor-Events werden an alle verbundenen Clients gepusht
- **Cross-Platform**: durchgehend `pathlib.Path`, kein shell-spezifischer Code, `tools/test_sensor.py` als CLI-unabhängiger Simulator
- **Erweiterbar**: neue Sensor-Typen via `SensorType`-Enum, neue Aktoren via `ActuatorType` + Handler

---

## Anforderungen

- [Docker](https://www.docker.com/) + Docker Compose **oder** Python 3.12+ (lokale Entwicklung)

---

## Schnellstart (Docker)

```bash
git clone https://github.com/9t29zhmwdh-coder/GardenFlow
cd GardenFlow
cp .env.example .env
docker compose up -d
```

Dashboard öffnen: **http://localhost:8000**

Sensordaten simulieren (plattformunabhängig):

```bash
pip install aiomqtt
python tools/test_sensor.py
```

---

## Lokale Entwicklung (ohne Docker)

```bash
# Linux / macOS
bash scripts/dev.sh

# Windows (PowerShell)
.\scripts\dev.ps1
```

---

## Architektur

```
MQTT-Broker (Mosquitto)
    │
    ▼  aiomqtt-Subscriber
Backend (FastAPI / Python 3.12)
    ├── MQTT-Client        — garden/# abonnieren → parsen → speichern + broadcast
    ├── Sensor-Repository  — SQLite (WAL) In-Memory-Cache + Verlauf
    ├── Logik-Engine       — Regeln bei jedem Sensor-Wert auswerten
    ├── Aktor-Controller   — MQTT-Befehle publizieren (Pumpe ein/aus)
    └── WebSocket-Registry — Events an alle Dashboard-Clients
    │
    ▼  StaticFiles-Mount
Frontend (Vanilla JS + Alpine.js + Chart.js)
    — direkt von FastAPI serviert, kein Build-Schritt
```

---

## MQTT-Topic-Schema

| Topic | Richtung | Payload |
|---|---|---|
| `garden/sensors/{zone}/{type}` | Gerät → Broker | `{"value": 42.5, "unit": "%"}` |
| `garden/actuators/{zone}/pump/set` | Broker → Gerät | `{"action": "on", "duration": 10}` |
| `garden/actuators/{zone}/pump/status` | Gerät → Broker | `{"state": "on"}` |

---

## API-Übersicht

| Methode | Pfad | Beschreibung |
|---|---|---|
| GET | `/api/sensors` | Alle aktuellen Sensor-Werte |
| GET | `/api/sensors/{zone}` | Sensor-Werte einer Zone |
| GET | `/api/history/{type}/{zone}` | Verlauf (`?hours=24`) |
| GET | `/api/rules` | Alle Regeln auflisten |
| POST | `/api/rules` | Neue Regel anlegen |
| PUT | `/api/rules/{id}` | Regel aktualisieren |
| DELETE | `/api/rules/{id}` | Regel löschen |
| POST | `/api/actuators/{zone}/pump` | Pumpe manuell steuern |
| GET | `/api/status` | System-Status |
| WS | `/ws` | Echtzeit-Sensor-Stream |

Vollständige interaktive Docs: **http://localhost:8000/docs**

---

## Beispiel: Automatisierungsregel anlegen

```bash
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Automatische Bewässerung bei Trockenheit",
    "conditions": [
      {"sensor_type": "moisture", "zone": "zone1", "operator": "<", "threshold": 30},
      {"sensor_type": "temperature", "zone": "zone1", "operator": ">", "threshold": 20}
    ],
    "condition_logic": "AND",
    "action": {"type": "activate_pump", "zone": "zone1", "duration_seconds": 10},
    "cooldown_seconds": 300
  }'
```

---

## Erweiterung

**Neuer Sensor-Typ:** Wert zu `SensorType`-Enum in `backend/sensors/models.py` und `backend/rules/models.py` hinzufügen.

**Neuer Aktor:** Handler in `backend/actuators/controller.py` ergänzen, in `ActionType` in `backend/rules/models.py` registrieren.


---

**Autor:** [Rafael Yilmaz](https://github.com/9t29zhmwdh-coder) · **Status:** Active · v0.1.0 · **Lizenz:** MIT

