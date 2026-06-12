from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


class SensorType(str, Enum):
    moisture    = "moisture"
    temperature = "temperature"
    humidity    = "humidity"
    light       = "light"


class Condition(BaseModel):
    sensor_type: SensorType
    zone:        str
    operator:    Literal["<", ">", "<=", ">=", "=="]
    threshold:   float


class ActionType(str, Enum):
    activate_pump   = "activate_pump"
    deactivate_pump = "deactivate_pump"
    send_alert      = "send_alert"


class Action(BaseModel):
    type:             ActionType
    zone:             str
    duration_seconds: Optional[int] = None
    message:          Optional[str] = None


class Rule(BaseModel):
    id:              str = Field(default_factory=lambda: str(uuid.uuid4()))
    name:            str
    enabled:         bool = True
    conditions:      list[Condition]
    condition_logic: Literal["AND", "OR"] = "AND"
    action:          Action
    cooldown_seconds: int = 300
    last_triggered:  Optional[datetime] = None


class RuleCreate(BaseModel):
    name:            str
    enabled:         bool = True
    conditions:      list[Condition]
    condition_logic: Literal["AND", "OR"] = "AND"
    action:          Action
    cooldown_seconds: int = 300
