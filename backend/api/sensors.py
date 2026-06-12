from fastapi import APIRouter, HTTPException, Query

from sensors.models import SensorReading, SensorType
from sensors.repository import get_history, get_latest_all, get_latest_zone

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("", response_model=list[SensorReading])
async def all_sensors():
    return get_latest_all()


@router.get("/{zone}", response_model=list[SensorReading])
async def zone_sensors(zone: str):
    readings = get_latest_zone(zone)
    if not readings:
        raise HTTPException(404, f"No readings for zone '{zone}'")
    return readings


@router.get("/history/{sensor_type}/{zone}", response_model=list[SensorReading])
async def history(
    sensor_type: SensorType,
    zone: str,
    hours: int = Query(default=24, ge=1, le=720),
):
    return await get_history(zone=zone, sensor_type=sensor_type, hours=hours)
