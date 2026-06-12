import aiosqlite
from pathlib import Path
from config import settings


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(settings.db_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db() -> None:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(settings.db_path) as db:
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
