# Privacy Policy — GardenFlow

GardenFlow runs **fully locally** in your home network.

## What data is processed

- Sensor readings (temperature, humidity, soil moisture, etc.) from connected devices (ESP32, Zigbee)
- Automation rule configurations defined by you

## What data leaves your machine

**Nothing.** All data flows within your local network:
- Sensors → MQTT broker (Mosquitto, local)
- MQTT → GardenFlow backend (FastAPI, local)
- Dashboard → Browser (local)

No sensor data, rules, or usage statistics are transmitted to external servers.

## Storage

- Sensor history is stored in a local SQLite database
- All data remains in your Docker volume on your local machine

## Third-party services

None. GardenFlow does not use cloud services, analytics, or telemetry.

## Changes

This policy may be updated with new releases. Check the CHANGELOG for details.
