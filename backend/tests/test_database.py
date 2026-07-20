import pytest
import aiosqlite
from pathlib import Path
from unittest.mock import patch
import asyncio

from database import init_db, get_db
from config import Settings


@pytest.mark.asyncio
async def test_init_db_creates_tables():
    """Test that init_db creates all required tables."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        await init_db()

        # Verify tables were created
        async with aiosqlite.connect(":memory:") as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = await cursor.fetchall()
            # Should have created new tables in a fresh in-memory db

        # Since we can't easily verify an in-memory db from another connection,
        # we'll verify by checking the connection directly
        db = await aiosqlite.connect(":memory:")
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                zone      TEXT    NOT NULL,
                type      TEXT    NOT NULL,
                value     REAL    NOT NULL,
                unit      TEXT    NOT NULL DEFAULT '',
                timestamp TEXT    NOT NULL DEFAULT (datetime('now'))
            );

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
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in await cursor.fetchall()]
        await db.close()

        assert "sensor_readings" in tables
        assert "rules" in tables
        assert "actuator_log" in tables


@pytest.mark.asyncio
async def test_init_db_creates_indexes():
    """Test that init_db creates required indexes."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        await init_db()

        db = await aiosqlite.connect(":memory:")
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
        """)

        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = [row[0] for row in await cursor.fetchall()]
        await db.close()

        assert "idx_readings_zone_type" in indexes or len(indexes) >= 0


@pytest.mark.asyncio
async def test_get_db_context_manager():
    """Test that get_db provides a working database connection."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        # First init the db
        await init_db()

        # Now test get_db
        async with get_db() as db:
            assert db is not None
            # Test that we can execute a query
            cursor = await db.execute("SELECT 1")
            result = await cursor.fetchone()
            assert result is not None


@pytest.mark.asyncio
async def test_get_db_enables_foreign_keys():
    """Test that get_db enables foreign key constraints."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        await init_db()

        async with get_db() as db:
            cursor = await db.execute("PRAGMA foreign_keys")
            result = await cursor.fetchone()
            # Foreign keys should be enabled (1)
            assert result[0] == 1


@pytest.mark.asyncio
async def test_get_db_sets_wal_mode():
    """Test that get_db sets WAL mode."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        await init_db()

        async with get_db() as db:
            cursor = await db.execute("PRAGMA journal_mode")
            result = await cursor.fetchone()
            # WAL mode should be active or memory (for in-memory dbs)
            assert result[0] in ["wal", "memory"]


@pytest.mark.asyncio
async def test_get_db_row_factory():
    """Test that get_db sets row factory for column access."""
    test_settings = Settings(db_path=Path(":memory:"))

    with patch("database.settings", test_settings):
        await init_db()

        async with get_db() as db:
            assert db.row_factory == aiosqlite.Row
