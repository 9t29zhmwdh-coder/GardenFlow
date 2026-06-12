import json
from datetime import datetime, timezone

import aiosqlite

from database import get_db
from rules.models import Rule, RuleCreate


async def list_rules() -> list[Rule]:
    rules: list[Rule] = []
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, enabled, conditions_json, condition_logic, "
            "action_json, cooldown_secs, last_triggered FROM rules"
        )
        async for row in cursor:
            rules.append(_row_to_rule(row))
    return rules


async def get_rule(rule_id: str) -> Rule | None:
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, enabled, conditions_json, condition_logic, "
            "action_json, cooldown_secs, last_triggered FROM rules WHERE id = ?",
            (rule_id,),
        )
        row = await cursor.fetchone()
    return _row_to_rule(row) if row else None


async def create_rule(data: RuleCreate) -> Rule:
    rule = Rule(**data.model_dump())
    async with await get_db() as db:
        await db.execute(
            """
            INSERT INTO rules (id, name, enabled, conditions_json, condition_logic,
                               action_json, cooldown_secs, last_triggered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (rule.id, rule.name, int(rule.enabled),
             json.dumps([c.model_dump() for c in rule.conditions]),
             rule.condition_logic,
             json.dumps(rule.action.model_dump()),
             rule.cooldown_seconds, None),
        )
        await db.commit()
    return rule


async def update_rule(rule_id: str, data: RuleCreate) -> Rule | None:
    existing = await get_rule(rule_id)
    if not existing:
        return None
    updated = Rule(id=rule_id, **data.model_dump(), last_triggered=existing.last_triggered)
    async with await get_db() as db:
        await db.execute(
            """
            UPDATE rules SET name=?, enabled=?, conditions_json=?, condition_logic=?,
                action_json=?, cooldown_secs=?
            WHERE id=?
            """,
            (updated.name, int(updated.enabled),
             json.dumps([c.model_dump() for c in updated.conditions]),
             updated.condition_logic,
             json.dumps(updated.action.model_dump()),
             updated.cooldown_seconds, rule_id),
        )
        await db.commit()
    return updated


async def delete_rule(rule_id: str) -> bool:
    async with await get_db() as db:
        cursor = await db.execute("DELETE FROM rules WHERE id=?", (rule_id,))
        await db.commit()
        return cursor.rowcount > 0


async def update_last_triggered(rule_id: str) -> None:
    async with await get_db() as db:
        await db.execute(
            "UPDATE rules SET last_triggered=? WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), rule_id),
        )
        await db.commit()


def _row_to_rule(row: aiosqlite.Row) -> Rule:
    return Rule(
        id=row["id"],
        name=row["name"],
        enabled=bool(row["enabled"]),
        conditions=json.loads(row["conditions_json"]),
        condition_logic=row["condition_logic"],
        action=json.loads(row["action_json"]),
        cooldown_seconds=row["cooldown_secs"],
        last_triggered=(
            datetime.fromisoformat(row["last_triggered"]).replace(tzinfo=timezone.utc)
            if row["last_triggered"] else None
        ),
    )
