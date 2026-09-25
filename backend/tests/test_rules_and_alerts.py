from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from actuators import controller
from rules.models import Action, ActionType


@pytest.mark.asyncio
async def test_alert_reaches_every_dashboard():
    with patch.object(controller.registry, "broadcast", new_callable=AsyncMock) as broadcast:
        await controller.execute_action(
            Action(type=ActionType.send_alert, zone="bed-1", message="Bed 1 is dry")
        )
    event = broadcast.await_args.args[0]
    assert event["type"] == "alert"
    assert event["zone"] == "bed-1"
    assert event["message"] == "Bed 1 is dry"
    assert "timestamp" in event


@pytest.fixture
def api(tmp_path: Path):
    """A TestClient with a real SQLite file and no MQTT broker."""
    with patch("database.settings.db_path", tmp_path / "garden.db"), \
         patch("main.mqtt_client.mqtt_loop", new_callable=AsyncMock):
        from main import app
        with TestClient(app) as client:
            yield client


# The exact shape the dashboard's rule editor sends (see formToRule in app.js).
EDITOR_RULE = {
    "name": "Water bed 1",
    "enabled": True,
    "condition_logic": "AND",
    "conditions": [
        {"sensor_type": "moisture", "zone": "bed-1", "operator": "<", "threshold": 30},
        {"sensor_type": "temperature", "zone": "bed-1", "operator": ">", "threshold": 25},
    ],
    "action": {"type": "activate_pump", "zone": "bed-1", "duration_seconds": 300, "message": None},
    "cooldown_seconds": 21600,
}


def test_editor_payload_creates_and_updates_a_rule(api):
    created = api.post("/api/rules", json=EDITOR_RULE)
    assert created.status_code == 201
    rule_id = created.json()["id"]

    alert = {
        **EDITOR_RULE,
        "action": {"type": "send_alert", "zone": "bed-1", "duration_seconds": None, "message": "Dry"},
        "cooldown_seconds": 5400,
    }
    updated = api.put(f"/api/rules/{rule_id}", json=alert)
    assert updated.status_code == 200

    (stored,) = api.get("/api/rules").json()
    assert stored["action"]["type"] == "send_alert"
    assert stored["action"]["message"] == "Dry"
    assert stored["cooldown_seconds"] == 5400
    assert len(stored["conditions"]) == 2


def test_rule_without_number_is_rejected_with_field_detail(api):
    broken = {**EDITOR_RULE, "conditions": [{**EDITOR_RULE["conditions"][0], "threshold": None}]}
    response = api.post("/api/rules", json=broken)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "threshold"
