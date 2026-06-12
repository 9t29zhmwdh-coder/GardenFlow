from typing import Optional
from pydantic import BaseModel


class PumpCommand(BaseModel):
    action:   str   # "on" | "off"
    duration: Optional[int] = None  # Sekunden (nur für "on")
    source:   str = "manual"
