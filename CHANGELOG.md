# Changelog — GardenFlow

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.1] — 2026-07-07

### Fixed
- MQTT subscriber never received messages on `aiomqtt>=2.3.0` (`client.messages()` was called as the old callable API instead of the current `client.messages` async iterator) — sensor data never reached the dashboard
- Every database call opened a connection twice (`async with await get_db()`), crashing with `RuntimeError: threads can only be started once` on rules/actuator endpoints
- Dashboard showed no sensor data after a page reload — the frontend only listened for live WebSocket events and never fetched current values via `/api/sensors` on load

## [0.1.0] — 2026-06-15

### Added
- MQTT broker integration (Mosquitto) for sensor/actuator communication
- Sensor data ingestion pipeline with SQLite storage
- Automation rule engine (condition-action rules)
- ESP32 and Zigbee sensor support
- Real-time web dashboard (FastAPI + WebSocket)
- Docker Compose deployment (Mosquitto + backend + frontend)
