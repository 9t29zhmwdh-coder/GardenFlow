import operator as op
import logging
from datetime import datetime, timezone

from rules.models import Condition, Rule
from rules.storage import list_rules, update_last_triggered
from sensors.models import SensorReading

logger = logging.getLogger("gardenflow.rules")

_OPERATORS = {
    "<":  op.lt,
    ">":  op.gt,
    "<=": op.le,
    ">=": op.ge,
    "==": op.eq,
}

# Injected at startup
_execute_action_fn = None


def set_action_executor(fn):
    global _execute_action_fn
    _execute_action_fn = fn


def _eval_condition(condition: Condition, reading: SensorReading) -> bool:
    if condition.sensor_type.value != reading.sensor_type.value:
        return False
    if condition.zone != reading.zone:
        return False
    fn = _OPERATORS.get(condition.operator)
    return fn(reading.value, condition.threshold) if fn else False


def _cooldown_ok(rule: Rule) -> bool:
    if rule.last_triggered is None:
        return True
    elapsed = (datetime.now(timezone.utc) - rule.last_triggered).total_seconds()
    return elapsed >= rule.cooldown_seconds


async def evaluate(reading: SensorReading) -> None:
    rules = await list_rules()
    for rule in rules:
        if not rule.enabled:
            continue
        if not _cooldown_ok(rule):
            continue

        results = [_eval_condition(c, reading) for c in rule.conditions]
        triggered = all(results) if rule.condition_logic == "AND" else any(results)

        if triggered:
            logger.info("Rule '%s' triggered by %s/%s=%.2f",
                        rule.name, reading.zone, reading.sensor_type.value, reading.value)
            if _execute_action_fn:
                await _execute_action_fn(rule.action)
            await update_last_triggered(rule.id)
