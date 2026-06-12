import asyncio
import logging
from datetime import datetime, timezone

import aiosqlite

from database import get_db
from mqtt.client import publish
from mqtt.topics import actuator_set_topic
from rules.models import Action, ActionType

logger = logging.getLogger("gardenflow.actuators")


async def execute_action(action: Action, source: str = "rule") -> None:
    if action.type == ActionType.activate_pump:
        await _pump_on(action.zone, duration=action.duration_seconds, source=source)
    elif action.type == ActionType.deactivate_pump:
        await _pump_off(action.zone, source=source)
    elif action.type == ActionType.send_alert:
        logger.warning("ALERT [%s]: %s", action.zone, action.message)


async def manual_pump(zone: str, action: str, duration: int | None, source: str = "manual") -> None:
    if action == "on":
        await _pump_on(zone, duration=duration, source=source)
    else:
        await _pump_off(zone, source=source)


async def _pump_on(zone: str, duration: int | None, source: str) -> None:
    topic = actuator_set_topic(zone, "pump")
    payload = {"action": "on", "duration": duration}
    await publish(topic, payload)
    await _log(zone, "pump", "on", source)
    logger.info("Pump ON zone=%s duration=%s", zone, duration)
    if duration:
        asyncio.create_task(_auto_off(zone, duration, source))


async def _pump_off(zone: str, source: str) -> None:
    topic = actuator_set_topic(zone, "pump")
    await publish(topic, {"action": "off"})
    await _log(zone, "pump", "off", source)
    logger.info("Pump OFF zone=%s", zone)


async def _auto_off(zone: str, delay: int, source: str) -> None:
    await asyncio.sleep(delay)
    await _pump_off(zone, source=f"{source}:auto_off")


async def _log(zone: str, actuator_type: str, action: str, source: str) -> None:
    async with await get_db() as db:
        await db.execute(
            "INSERT INTO actuator_log (zone, type, action, source, timestamp) VALUES (?, ?, ?, ?, ?)",
            (zone, actuator_type, action, source, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
