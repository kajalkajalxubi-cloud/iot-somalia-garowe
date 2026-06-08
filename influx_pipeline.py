import time
import random
import math
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Database Connection Parameters
TOKEN = "MasterPassword2026!"  # Uses basic init profiles from compose config
ORG = "GlobalIoT"
BUCKET = "telemetry"
URL = "http://localhost:8086"

# Simulation Profiles
REGIONS = {
    "North_America": {"lat": 40.7128, "lon": -74.0060, "base": 5400000000},
    "Europe": {"lat": 48.8566, "lon": 2.3522, "base": 4200000000},
    "Asia_Pacific": {"lat": 35.6762, "lon": 139.6503, "base": 6100000000}
}
BIC_OPERATORS = ["MSKU", "MSCU", "HLXU", "CMAU", "COSU"]
PORT_GEOFENCES = {
    "Port_of_Shanghai": {"lat": 31.2304, "lon": 121.4737, "code": "CNSHA"},
    "Port_of_Rotterdam": {"lat": 51.9244, "lon": 4.4777, "code": "NLRTM"},
    "Port_of_Los_Angeles": {"lat": 33.7432, "lon": -118.2673, "code": "USLAX"}
}

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def run_pipeline():
    print("🚀 Real-Time InfluxDB Pipeline is broadcasting...")
    while True:
        try:
            # 1. Pipeline Macro Global Data Points
            for reg, conf in REGIONS.items():
                drift = random.uniform(-0.002, 0.002)
                point = Point("global_iot") \
                    .tag("region", reg) \
                    .field("active_nodes", int(conf["base"] * (1 + drift))) \
                    .field("bandwidth_tbps", round(random.uniform(30.2, 55.7), 2)) \
                    .time(time.time_ns(), WritePrecision.NS)
                write_api.write(bucket=BUCKET, org=ORG, record=point)

            # 2. Pipeline BIC Smart Cargo Container Events
            port_name = random.choice(list(PORT_GEOFENCES.keys()))
            port = PORT_GEOFENCES[port_name]
            container_id = f"{random.choice(BIC_OPERATORS)}{random.randint(100000, 999999)}-{random.randint(0,9)}"
            door_locked = random.choice([True, True, True, False])
            
            bic_point = Point("bic_shipping") \
                .tag("container_id", container_id) \
                .tag("facility_code", port["code"]) \
                .field("lat", round(port["lat"] + random.uniform(-0.02, 0.02), 5)) \
                .field("lon", round(port["lon"] + random.uniform(-0.02, 0.02), 5)) \
                .field("temperature_c", round(random.uniform(-20.0, -18.0) if random.choice([True, False]) else random.uniform(19.0, 24.0), 1)) \
                .field("door_secure", 1 if door_locked else 0) \
                .field("tamper_alert", 1 if not door_locked else 0) \
                .time(time.time_ns(), WritePrecision.NS)
            
            write_api.write(bucket=BUCKET, org=ORG, record=bic_point)
            print(f"📡 Dispatched telematics package for container: {container_id}")
            time.sleep(1)
            
        except Exception as err:
            print(f"⚠️ Insertion failure: {err}")
            time.sleep(5)

if __name__ == "__main__":
    run_pipeline()
