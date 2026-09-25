import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from actuators.controller import execute_action
from api.actuators import router as actuators_router
from api.rules import router as rules_router
from api.sensors import router as sensors_router
from api.status import router as status_router
from api.websocket import registry
from database import init_db
from mqtt import client as mqtt_client
from rules.engine import evaluate, set_action_executor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("gardenflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    mqtt_client.set_broadcast(registry.broadcast)
    mqtt_client.set_rule_engine(evaluate)
    set_action_executor(execute_action)
    asyncio.create_task(mqtt_client.mqtt_loop())
    logger.info("GardenFlow started")
    yield
    logger.info("GardenFlow stopped")


app = FastAPI(
    title="GardenFlow",
    description="Modular Home Garden Automation Toolkit",
    version="1.0.8",
    lifespan=lifespan,
)

# No CORS middleware on purpose: the dashboard is served from this same
# origin, and the API has no login. A wildcard CORS policy let any website
# open in the same browser switch pumps and delete rules in the background.

app.include_router(sensors_router)
app.include_router(actuators_router)
app.include_router(rules_router)
app.include_router(status_router)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await registry.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        registry.disconnect(ws)


# Serve frontend from /; registered last since it mounts at root and would
# otherwise catch every path (including /ws) before more specific routes,
# crashing the WebSocket handshake with a 500 (StaticFiles only handles
# the ASGI "http" scope, not "websocket").
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
