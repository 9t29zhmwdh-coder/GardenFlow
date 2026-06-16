# Architecture — GardenFlow

## Overview

GardenFlow is a Python/FastAPI application with MQTT integration, deployed via Docker Compose.

```
GardenFlow/
├── backend/
│   ├── main.py             # FastAPI app, WebSocket endpoint
│   ├── mqtt_client.py      # MQTT subscriber (paho-mqtt)
│   ├── rule_engine.py      # Automation rule evaluator
│   ├── db.py               # SQLite storage (aiosqlite)
│   └── models.py           # Pydantic data models
├── frontend/
│   ├── index.html          # Real-time dashboard
│   └── static/             # JS, CSS
├── sensors/
│   └── esp32/              # Example ESP32 firmware (Arduino)
├── docker-compose.yml      # Full stack: mosquitto + backend + frontend
├── mosquitto/
│   └── mosquitto.conf      # MQTT broker config
├── pyproject.toml
└── README.md
```

## Data Flow

1. **Sensors** (ESP32, Zigbee) publish readings to MQTT topics (e.g., `garden/sensor/soil_moisture`)
2. **Mosquitto** broker receives and routes messages
3. **mqtt_client** subscribes, parses, and writes readings to SQLite
4. **rule_engine** evaluates automation rules (e.g., "if soil_moisture < 30% → trigger pump")
5. **FastAPI** exposes REST API + WebSocket for the dashboard
6. **Dashboard** displays real-time sensor data, rule status, and history charts

## MQTT Topic Convention

```
garden/sensor/<sensor_id>/<metric>
garden/actuator/<actuator_id>/command
garden/actuator/<actuator_id>/status
```

## Supported Protocols

| Protocol | Use Case |
|----------|----------|
| MQTT (Mosquitto) | Primary sensor/actuator bus |
| ESP32 (WiFi) | DIY sensors and actuators |
| Zigbee (via Zigbee2MQTT) | Commercial sensors |
| WebSocket | Real-time dashboard updates |
