# Architecture, GardenFlow

## Overview

GardenFlow is a Python/FastAPI application with MQTT integration, deployed via Docker Compose.

```
GardenFlow/
├── backend/
│   ├── main.py                # FastAPI app, startup wiring
│   ├── config.py               # pydantic-settings configuration
│   ├── database.py             # SQLite storage (aiosqlite)
│   ├── requirements.txt
│   ├── mqtt/
│   │   ├── client.py           # MQTT subscriber (aiomqtt)
│   │   └── topics.py           # topic parsing/wildcards
│   ├── sensors/
│   │   ├── models.py           # SensorReading, SensorType
│   │   └── repository.py       # persistence for sensor readings
│   ├── actuators/
│   │   ├── models.py           # ActuatorType, actuator state
│   │   └── controller.py       # actuator command dispatch
│   ├── rules/
│   │   ├── models.py           # rule definitions
│   │   ├── engine.py           # automation rule evaluator
│   │   └── storage.py          # rule persistence
│   └── api/
│       ├── sensors.py          # sensor REST endpoints
│       ├── actuators.py        # actuator REST endpoints
│       ├── rules.py            # rule management REST endpoints
│       ├── status.py           # health/status endpoint
│       └── websocket.py        # real-time dashboard push
├── frontend/
│   ├── index.html              # real-time dashboard (no build step)
│   └── assets/                 # app.js, style.css
├── mosquitto/
│   └── config/
│       └── mosquitto.conf      # MQTT broker config
├── tools/
│   └── test_sensor.py          # cross-platform CLI sensor simulator
└── docker-compose.yml          # full stack: mosquitto + backend + frontend
```

## Data Flow

1. **Sensors** (ESP32, Zigbee, or the `tools/test_sensor.py` simulator) publish readings to MQTT topics under `garden/sensors/<zone>/<type>`
2. **Mosquitto** broker receives and routes messages
3. **backend/mqtt/client.py** subscribes via `aiomqtt`, parses readings, and writes them through `sensors/repository.py` into SQLite
4. **backend/rules/engine.py** evaluates automation rules (e.g., "if soil_moisture < 30% -> trigger pump") and dispatches actions via `actuators/controller.py`
5. **FastAPI** (`backend/api/`) exposes REST endpoints and a WebSocket stream for the dashboard
6. **Dashboard** (`frontend/index.html` + `assets/app.js`) displays real-time sensor data, rule status, and history charts via Chart.js

## MQTT Topic Convention

```
garden/sensors/<zone>/<type>
garden/actuators/<zone>/<type>/command
```

## Supported Protocols

| Protocol | Use Case |
|----------|----------|
| MQTT (Mosquitto) | Primary sensor/actuator bus |
| ESP32 (WiFi) | DIY sensors and actuators, publish over MQTT directly (no bundled firmware in this repo) |
| Zigbee (via Zigbee2MQTT) | Commercial sensors, bridged to MQTT |
| WebSocket | Real-time dashboard updates |
