# Roadmap, GardenFlow

## v0.1.0, Initial Release (2026-06-15)
- [x] MQTT broker integration (Mosquitto)
- [x] Sensor data ingestion and SQLite storage
- [x] Automation rule engine
- [x] ESP32 and Zigbee sensor support
- [x] Real-time dashboard (FastAPI + WebSocket)
- [x] Docker Compose deployment

## v0.2.0, Planned
- [ ] Rule editor UI (no config file editing)
- [ ] Historical charts (7d, 30d views)
- [ ] Push notifications (ntfy / Gotify)
- [ ] Multi-zone support (greenhouse, beds, pots)

## v0.3.0, Planned
- [ ] Weather API integration (offline: open-meteo)
- [ ] Predictive watering (simple ML model)
- [ ] Mobile-optimized dashboard

## v1.0.0, Target
- [ ] Full test coverage
- [ ] Helm chart for Kubernetes deployment
- [ ] Plugin system for custom sensor adapters

## Dual-Licensing Readiness

Assessed 2026-07-11: Community-only, not a Dual-Licensing candidate. GardenFlow is a consumer/hobbyist home-garden automation toolkit with no enterprise audience and no team or multi-tenant dimension anywhere on the roadmap. This category (maker-focused home automation, in the same space as Home Assistant) conventionally stays fully open source rather than dual-licensed. Revisit only if a genuine commercial-greenhouse or multi-site use case emerges.
