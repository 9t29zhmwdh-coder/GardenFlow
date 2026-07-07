from datetime import datetime, timezone
from typing import Optional

import aiosqlite

from database import get_db
from sensors.models import SensorReading, SensorType

# In-memory cache: latest reading per (zone, type)
_latest: dict[tuple[str, str], SensorReading] = {}


async def upsert_reading(reading: SensorReading) -> None:
    _latest[(reading.zone, reading.sensor_type.value)] = reading
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO sensor_readings (zone, type, value, unit, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (reading.zone, reading.sensor_type.value, reading.value,
             reading.unit, reading.timestamp.isoformat()),
        )
        await db.commit()


def get_latest_all() -> list[SensorReading]:
    return list(_latest.values())


def get_latest_zone(zone: str) -> list[SensorReading]:
    return [r for (z, _), r in _latest.items() if z == zone]


async def get_history(
    zone: str,
    sensor_type: SensorType,
    hours: int = 24,
) -> list[SensorReading]:
    rows: list[SensorReading] = []
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, zone, type, value, unit, timestamp
            FROM sensor_readings
            WHERE zone = ? AND type = ?
              AND timestamp >= datetime('now', ? || ' hours')
            ORDER BY timestamp ASC
            """,
            (zone, sensor_type.value, f"-{hours}"),
        )
        async for row in cursor:
            rows.append(SensorReading(
                id=row["id"],
                zone=row["zone"],
                sensor_type=SensorType(row["type"]),
                value=row["value"],
                unit=row["unit"],
                timestamp=datetime.fromisoformat(row["timestamp"]).replace(tzinfo=timezone.utc),
            ))
    return rows
