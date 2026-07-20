import pytest
import aiosqlite
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from config import Settings
from main import app
from database import init_db, get_db


@pytest.fixture
def test_settings():
    """Provide test settings with in-memory SQLite database."""
    return Settings(
        mqtt_host="localhost",
        mqtt_port=1883,
        db_path=Path(":memory:"),  # In-memory database for testing
        debug=True,
    )


@pytest.fixture
async def test_db(test_settings):
    """Provide an in-memory test database with schema."""
    # Mock settings
    with patch("database.settings", test_settings):
        with patch("config.settings", test_settings):
            # Create in-memory database
            db = await aiosqlite.connect(":memory:")
            db.row_factory = aiosqlite.Row

            try:
                # Initialize schema
                await db.execute("PRAGMA journal_mode=WAL")
                await db.executescript("""
                    CREATE TABLE IF NOT EXISTS sensor_readings (
                        id        INTEGER PRIMARY KEY AUTOINCREMENT,
                        zone      TEXT    NOT NULL,
                        type      TEXT    NOT NULL,
                        value     REAL    NOT NULL,
                        unit      TEXT    NOT NULL DEFAULT '',
                        timestamp TEXT    NOT NULL DEFAULT (datetime('now'))
                    );

                    CREATE INDEX IF NOT EXISTS idx_readings_zone_type
                        ON sensor_readings (zone, type, timestamp DESC);

                    CREATE TABLE IF NOT EXISTS rules (
                        id              TEXT PRIMARY KEY,
                        name            TEXT NOT NULL,
                        enabled         INTEGER NOT NULL DEFAULT 1,
                        conditions_json TEXT NOT NULL,
                        condition_logic TEXT NOT NULL DEFAULT 'AND',
                        action_json     TEXT NOT NULL,
                        cooldown_secs   INTEGER NOT NULL DEFAULT 300,
                        last_triggered  TEXT
                    );

                    CREATE TABLE IF NOT EXISTS actuator_log (
                        id        INTEGER PRIMARY KEY AUTOINCREMENT,
                        zone      TEXT NOT NULL,
                        type      TEXT NOT NULL,
                        action    TEXT NOT NULL,
                        source    TEXT NOT NULL DEFAULT 'manual',
                        timestamp TEXT NOT NULL DEFAULT (datetime('now'))
                    );
                """)
                await db.commit()

                yield db
            finally:
                await db.close()


@pytest.fixture
def client():
    """Provide a FastAPI TestClient with mocked MQTT and lifespan."""
    with patch("main.mqtt_client") as mock_mqtt, \
         patch("main.registry") as mock_registry:

        mock_mqtt.set_broadcast = AsyncMock()
        mock_mqtt.set_rule_engine = AsyncMock()
        mock_mqtt.mqtt_loop = AsyncMock()
        mock_registry.broadcast = AsyncMock()
        mock_registry.client_count = 0

        with patch("database.settings.db_path", Path(":memory:")):
            return TestClient(app)


@pytest.fixture
async def mock_mqtt():
    """Mock MQTT client."""
    with patch("main.mqtt_client") as mock:
        mock.set_broadcast = AsyncMock()
        mock.set_rule_engine = AsyncMock()
        mock.mqtt_loop = AsyncMock()
        yield mock
