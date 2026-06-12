from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class SensorType(str, Enum):
    moisture    = "moisture"      # Bodenfeuchte %
    temperature = "temperature"   # °C
    humidity    = "humidity"      # Luftfeuchtigkeit %
    light       = "light"         # Lux


class SensorReading(BaseModel):
    id:          int | None = None
    zone:        str
    sensor_type: SensorType
    value:       float
    unit:        str = ""
    timestamp:   datetime
