SENSOR_READING = "garden/sensors/{zone}/{sensor_type}"
ACTUATOR_STATUS = "garden/actuators/{zone}/{actuator_type}/status"
ACTUATOR_SET    = "garden/actuators/{zone}/{actuator_type}/set"
SYSTEM_STATUS   = "garden/system/status"
WILDCARD_ALL    = "garden/#"


def sensor_topic(zone: str, sensor_type: str) -> str:
    return SENSOR_READING.format(zone=zone, sensor_type=sensor_type)


def actuator_set_topic(zone: str, actuator_type: str) -> str:
    return ACTUATOR_SET.format(zone=zone, actuator_type=actuator_type)


def parse_sensor_topic(topic: str) -> tuple[str, str] | None:
    """Returns (zone, sensor_type) or None if topic doesn't match."""
    parts = topic.split("/")
    if len(parts) == 4 and parts[0] == "garden" and parts[1] == "sensors":
        return parts[2], parts[3]
    return None
