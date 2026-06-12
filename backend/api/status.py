from fastapi import APIRouter

from api.websocket import registry
from sensors.repository import get_latest_all

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
async def status():
    readings = get_latest_all()
    zones = sorted({r.zone for r in readings})
    return {
        "status": "ok",
        "ws_clients": registry.client_count,
        "zones": zones,
        "sensor_count": len(readings),
    }


@router.get("/health")
async def health():
    return {"status": "ok"}
