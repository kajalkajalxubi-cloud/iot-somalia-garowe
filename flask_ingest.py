from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# In-memory storage block for serverless compatibility
telemetry_storage = []

@app.route('/')
def home():
    return "<h1>Flask Backend is Running Successfully!</h1>"

@app.route("/api/ingest", methods=["POST"])
def ingest():
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON required"}), 400
        
    payload = request.get_json()
    rows = payload if isinstance(payload, list) else [payload]
    now = datetime.utcnow().isoformat() + "Z"
    
    for row in rows:
        telemetry_storage.append({
            "device_id": row.get("device_id", "unknown"),
            "timestamp": row.get("timestamp") or now,
            "metric": row.get("metric", "unknown"),
            "value": float(row.get("value", 0)) if row.get("value") is not None else 0.0,
            "unit": row.get("unit", ""),
            "status": row.get("status", ""),
            "created_at": now
        })
    
    # Keep local storage size controlled
    if len(telemetry_storage) > 1000:
        del telemetry_storage[:len(telemetry_storage) - 500]
        
    return jsonify({"status": "ok", "rows": len(rows)}), 201

@app.route("/api/latest", methods=["GET"])
def latest():
    minutes = int(request.args.get("minutes", 10))
    threshold = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat() + "Z"
    
    # Filter incoming historical readings safely
    filtered_data = [
        row for row in telemetry_storage 
        if row["timestamp"] >= threshold
    ]
    
    # Sort data showing newest updates first
    filtered_data.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return jsonify({"status": "ok", "data": filtered_data[:500]})

if __name__ == '__main__':
    app.run(debug=True)
