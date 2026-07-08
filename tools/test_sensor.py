"""
Sensor-Simulator, plattformunabhängig (Linux, Windows, macOS).
Sendet zufällige Sensor-Werte via MQTT an den lokalen Broker.

Verwendung:
    pip install aiomqtt
    python tools/test_sensor.py
    python tools/test_sensor.py --host localhost --port 1883 --zone zone2 --count 20
"""
import argparse
import asyncio
import json
import random
from datetime import datetime, timezone


async def simulate(host: str, port: int, zone: str, count: int, interval: float) -> None:
    try:
        import aiomqtt
    except ImportError:
        print("aiomqtt nicht installiert. Bitte: pip install aiomqtt")
        return

    sensors = [
        ("moisture",    (10, 90),  "%"),
        ("temperature", (5,  40),  "°C"),
        ("humidity",    (20, 95),  "%"),
        ("light",       (0, 100000), "lux"),
    ]

    print(f"Verbinde mit MQTT {host}:{port} …")
    async with aiomqtt.Client(host, port) as client:
        print(f"Sende {count} Lesungen für Zone '{zone}' (Interval {interval}s), Ctrl+C zum Beenden\n")
        for i in range(count):
            for sensor_type, (lo, hi), unit in sensors:
                value = round(random.uniform(lo, hi), 2)
                topic = f"garden/sensors/{zone}/{sensor_type}"
                payload = json.dumps({
                    "value": value,
                    "unit": unit,
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
                await client.publish(topic, payload)
                print(f"  [{sensor_type:12}] {value:8.2f} {unit}")
            print(f"--- Lesung {i + 1}/{count} ---")
            if i < count - 1:
                await asyncio.sleep(interval)
    print("\nFertig.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GardenFlow Sensor-Simulator")
    parser.add_argument("--host",     default="localhost")
    parser.add_argument("--port",     type=int, default=1883)
    parser.add_argument("--zone",     default="zone1")
    parser.add_argument("--count",    type=int, default=10)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    asyncio.run(simulate(args.host, args.port, args.zone, args.count, args.interval))
