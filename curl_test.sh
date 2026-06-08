#!/usr/bin/env bash
# Example curl test to post sample telemetry to the Flask ingest service
# Replace <HOST> with your PC IP (e.g., 192.168.1.100)

HOST="127.0.0.1"
PORT=5000
URL="http://${HOST}:${PORT}/api/ingest"

cat <<EOF | curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST -H "Content-Type: application/json" -d @- "$URL"
[
  {
    "device_id": "TEST_NODE",
    "timestamp": "$(date -u +%s)",
    "metric": "battery_voltage",
    "value": 12.34,
    "unit": "V",
    "status": ""
  },
  {
    "device_id": "TEST_NODE",
    "timestamp": "$(date -u +%s)",
    "metric": "battery_percent",
    "value": 87,
    "unit": "%",
    "status": ""
  }
]
EOF
