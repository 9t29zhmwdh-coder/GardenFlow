import asyncio
import json
import logging
from datetime import datetime, timezone

import aiomqtt

from config import settings
from mqtt.topics import WILDCARD_ALL, parse_sensor_topic
from sensors.models import SensorReading, SensorType
from sensors.repository import upsert_reading

logger = logging.getLogger("gardenflow.mqtt")

# Injected at startup from main.py
_broadcast_fn = None
_rule_engine_fn = None


def set_broadcast(fn):
    global _broadcast_fn
    _broadcast_fn = fn


def set_rule_engine(fn):
    global _rule_engine_fn
    _rule_engine_fn = fn


async def mqtt_loop() -> None:
    """Persistent MQTT listener with auto-reconnect."""
    reconnect_delay = 5
    while True:
        try:
            async with aiomqtt.Client(settings.mqtt_host, settings.mqtt_port) as client:
                logger.info("MQTT connected to %s:%d", settings.mqtt_host, settings.mqtt_port)
                reconnect_delay = 5
                async with client.messages() as messages:
                    await client.subscribe(WILDCARD_ALL)
                    async for message in messages:
                        await _handle_message(str(message.topic), message.payload)
        except aiomqtt.MqttError as exc:
            logger.warning("MQTT disconnected (%s) — reconnecting in %ds", exc, reconnect_delay)
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)
        except Exception:
            logger.exception("Unexpected MQTT error")
            await asyncio.sleep(reconnect_delay)


async def _handle_message(topic: str, payload: bytes) -> None:
    try:
        data = json.loads(payload.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.debug("Non-JSON payload on %s — ignored", topic)
        return

    parsed = parse_sensor_topic(topic)
    if parsed is None:
        return

    zone, sensor_type_str = parsed
    try:
        sensor_type = SensorType(sensor_type_str)
    except ValueError:
        logger.debug("Unknown sensor type '%s' — ignored", sensor_type_str)
        return

    reading = SensorReading(
        zone=zone,
        sensor_type=sensor_type,
        value=float(data.get("value", 0)),
        unit=str(data.get("unit", "")),
        timestamp=datetime.now(timezone.utc),
    )

    await upsert_reading(reading)

    event = {
        "type": "sensor",
        "zone": zone,
        "sensor_type": sensor_type.value,
        "value": reading.value,
        "unit": reading.unit,
        "timestamp": reading.timestamp.isoformat(),
    }

    if _broadcast_fn:
        await _broadcast_fn(event)

    if _rule_engine_fn:
        await _rule_engine_fn(reading)


async def publish(topic: str, payload: dict) -> None:
    try:
        async with aiomqtt.Client(settings.mqtt_host, settings.mqtt_port) as client:
            await client.publish(topic, json.dumps(payload))
    except aiomqtt.MqttError as exc:
        logger.error("Failed to publish to %s: %s", topic, exc)
