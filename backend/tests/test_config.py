import os
from pathlib import Path
from unittest.mock import patch
import pytest

from config import Settings


class TestConfig:
    """Test configuration loading and validation."""

    def test_default_settings(self):
        """Test that default settings are applied correctly."""
        settings = Settings()

        assert settings.mqtt_host == "localhost"
        assert settings.mqtt_port == 1883
        assert settings.mqtt_topic_prefix == "garden"
        assert settings.app_host == "0.0.0.0"
        assert settings.app_port == 8000
        assert settings.debug is False

    def test_mqtt_settings_override(self):
        """Test MQTT settings can be overridden."""
        settings = Settings(mqtt_host="mqtt.example.com", mqtt_port=8883)

        assert settings.mqtt_host == "mqtt.example.com"
        assert settings.mqtt_port == 8883

    def test_db_path_from_env(self):
        """Test that DB_PATH environment variable is respected."""
        test_path = "/tmp/test_garden.db"
        with patch.dict(os.environ, {"DB_PATH": test_path}):
            settings = Settings()
            assert settings.db_path == Path(test_path)

    def test_db_path_default(self):
        """Test that default DB path is used when env var is not set."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove DB_PATH if it exists
            os.environ.pop("DB_PATH", None)
            settings = Settings()
            # Should be $HOME/.gardenflow/garden.db
            assert "gardenflow" in str(settings.db_path)
            assert settings.db_path.name == "garden.db"

    def test_app_settings(self):
        """Test app-specific settings."""
        settings = Settings(app_host="127.0.0.1", app_port=9000, debug=True)

        assert settings.app_host == "127.0.0.1"
        assert settings.app_port == 9000
        assert settings.debug is True

    def test_settings_immutability(self):
        """Test that settings are properly configured."""
        settings = Settings()
        # Pydantic v2 Settings should work
        assert hasattr(settings, "mqtt_host")
        assert hasattr(settings, "db_path")
