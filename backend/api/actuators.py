from fastapi import APIRouter

from actuators.controller import manual_pump
from actuators.models import PumpCommand

router = APIRouter(prefix="/api/actuators", tags=["actuators"])


@router.post("/{zone}/pump")
async def pump_control(zone: str, cmd: PumpCommand):
    await manual_pump(
        zone=zone,
        action=cmd.action,
        duration=cmd.duration,
        source=cmd.source,
    )
    return {"status": "ok", "zone": zone, "action": cmd.action}
