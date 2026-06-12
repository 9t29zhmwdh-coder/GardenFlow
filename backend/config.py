import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "garden"

    db_path: Path = Path(os.getenv("DB_PATH", Path.home() / ".gardenflow" / "garden.db"))

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
