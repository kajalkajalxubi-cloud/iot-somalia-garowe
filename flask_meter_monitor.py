from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

latest_meter_reading = {
    "meter_id": "NECSOM-GW-9942",
    "timestamp": "N/A",
    "voltage_v": 230.0,
    "current_a": 0.0,
    "active_power_kw": 0.0,
    "power_factor": 1.0,
    "remaining_credit_kwh": 45.2,
}

TRANSLATIONS = {
    'en': {
        'title': 'Real-Time Utility Monitor',
        'connected': 'Device Connected',
        'voltage': 'LINE VOLTAGE',
        'current': 'ACTIVE CURRENT',
        'load': 'ACTIVE LOAD',
        'balance': 'REMAINING BALANCE'
    },
    'so': {
        'title': 'Kormeerka Korontada ee Waqtiga Real-Time ah',
        'connected': 'Aaladda Ku Xiran',
        'voltage': 'CORONTADA KHADKA',
        'current': 'HAYBTA CURRENT-KA',
        'load': 'XAMILKA LABAADIYAH',
        'balance': 'HARAGA HARAY'
    }
}

# Sample events for calendar
SAMPLE_EVENTS = [
    {
        "id": "1",
        "title": "Network maintenance",
        "start": "2026-06-03T09:00:00",
        "end": "2026-06-03T11:00:00",
        "time": "09:00 - 11:00"
    },
    {
        "id": "2",
        "title": "Load balancing review",
        "start": "2026-06-06T13:00:00",
        "end": "2026-06-06T14:00:00",
        "time": "13:00 - 14:00"
    },
    {
        "id": "3",
        "title": "Firmware update",
        "start": "2026-06-12T14:00:00",
        "end": "2026-06-12T15:00:00",
        "time": "14:00 - 15:00"
    }
]
EVENT_COUNTER = len(SAMPLE_EVENTS) + 1

@app.route('/')
def dashboard_home():
    lang = request.args.get('lang', 'en')
    texts = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return f"""
    <!DOCTYPE html>
    <html lang=\"{lang}\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>{texts['title']}</title>
        <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
        <script>
            let iotChart = null;
            
            async function refreshData() {{
                try {{
                    const response = await fetch('/api/telemetry');
                    if (!response.ok) {{
                        throw new Error('Failed to fetch telemetry');
                    }}
                    const data = await response.json();
                    document.getElementById('meter_id').innerText = data.meter_id;
                    document.getElementById('time').innerText = data.timestamp;
                    document.getElementById('voltage').innerText = data.voltage_v + ' V';
                    document.getElementById('current').innerText = data.current_a + ' A';
                    document.getElementById('power').innerText = data.active_power_kw + ' kW';
                    document.getElementById('credit').innerText = data.remaining_credit_kwh + ' kWh';
                }} catch (error) {{
                    console.warn(error);
                }}
            }}

            function changeLanguage(lang) {{
                const query = new URLSearchParams(window.location.search);
                query.set('lang', lang);
                window.location.search = query.toString();
            }}

            function viewMetricDetails(metricType) {{
                alert('Fetching breakdown history for: ' + metricType.toUpperCase() + ' from the Garowe Gateway...');
                fetch('/api/system-details')
                    .then(response => response.json())
                    .then(data => {{
                        console.log('Full System Specs:', data);
                        const details = `Location: ${data.location}\nGateway: ${data.gateway_status}\nSignal: ${data.signal_strength}\nFirmware: ${data.firmware_version}`;
                        alert(details);
                    }})
                    .catch(error => console.warn('System details fetch failed:', error));
            }}

            function initChart() {{
                const ctx = document.getElementById('iotLiveChart').getContext('2d');
                iotChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: [],
                        datasets: [{{
                            label: 'Voltage (V)',
                            data: [],
                            borderColor: '#3498db',
                            borderWidth: 2,
                            fill: false,
                            yAxisID: 'y',
                            tension: 0.3
                        }}, {{
                            label: 'Power (kW)',
                            data: [],
                            borderColor: '#e74c3c',
                            borderWidth: 2,
                            fill: false,
                            yAxisID: 'y1',
                            tension: 0.3
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        interaction: {{ mode: 'index', intersect: false }},
                        scales: {{
                            y: {{ type: 'linear', display: true, position: 'left', title: {{ display: true, text: 'Voltage (V)' }} }},
                            y1: {{ type: 'linear', display: true, position: 'right', title: {{ display: true, text: 'Power (kW)' }}, grid: {{ drawOnChartArea: false }} }}
                        }},
                        plugins: {{
                            legend: {{ display: true, position: 'top' }},
                            title: {{ display: false }}
                        }}
                    }}
                }});
            }}

            function updateChartData() {{
                if (!iotChart) return;
                fetch('/api/metrics')
                    .then(response => response.json())
                    .then(data => {{
                        const timeNow = new Date().toLocaleTimeString();
                        
                        if(iotChart.data.labels.length > 20) {{
                            iotChart.data.labels.shift();
                            iotChart.data.datasets[0].data.shift();
                            iotChart.data.datasets[1].data.shift();
                        }}
                        
                        iotChart.data.labels.push(timeNow);
                        iotChart.data.datasets[0].data.push(data.voltage_v || 0);
                        iotChart.data.datasets[1].data.push(data.active_power_kw || 0);
                        iotChart.update();
                    }})
                    .catch(error => console.warn('Metrics fetch failed:', error));
            }}

            function fetchLiveTelemetry() {{
                fetch('/api/metrics')
                    .then(res => res.json())
                    .then(data => {{
                        document.getElementById('live-voltage-display').innerText = (data.voltage_v || 0) + ' V';
                        document.getElementById('live-current-display').innerText = (data.current_a || 0) + ' A';
                        document.getElementById('live-power-display').innerText = (data.active_power_kw || 0) + ' kW';
                    }})
                    .catch(error => console.warn('Live telemetry fetch failed:', error));
            }}

            setInterval(refreshData, 3000);
            setInterval(updateChartData, 3000);
            setInterval(fetchLiveTelemetry, 3000);
            window.addEventListener('load', () => {{
                refreshData();
                initChart();
                updateChartData();
                fetchLiveTelemetry();
            }});
        </script>
        <style>
            body {{ font-family: Inter, system-ui, sans-serif; background: linear-gradient(180deg, #eef2ff 0%, #f8fafc 100%); color: #111827; margin: 0; padding: 0; }}
            .page-shell {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
            .top-bar {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; }}
            .language-selector label {{ font-weight: 600; margin-right: 8px; }}
            .language-selector select {{ padding: 8px 10px; border-radius: 10px; border: 1px solid #cbd5e1; background: #fff; color: #111827; }}
            .hero {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 28px; box-shadow: 0 20px 60px rgba(15, 23, 42, 0.08); }}
            .hero h1 {{ margin: 0 0 12px; font-size: clamp(2rem, 3vw, 3rem); }}
            .hero p {{ margin: 0; color: #475569; font-size: 1rem; }}
            .status-block {{ margin-top: 18px; font-size: 0.98rem; color: #334155; }}
            .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 24px; }}
            .card {{ background: #fff; border-radius: 22px; padding: 24px; border: 1px solid transparent; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08); transition: transform 180ms ease, border-color 180ms ease; cursor: pointer; }}
            .card:hover {{ transform: translateY(-4px); border-color: #c7d2fe; }}
            .card h3 {{ margin: 0 0 10px; font-size: 0.95rem; letter-spacing: 0.12em; text-transform: uppercase; color: #334155; }}
            .card p {{ margin: 0; font-size: 2.25rem; font-weight: 700; color: #1d4ed8; }}
            .footer-note {{ margin-top: 24px; color: #475569; font-size: 0.95rem; }}
        </style>
    </head>
    <body>
        <div class="page-shell">
            <div class="top-bar">
                <div class="language-selector">
                    <label for="langSelect">Language / Luqadda:</label>
                    <select id="langSelect" onchange="changeLanguage(this.value)">
                        <option value="en" {'selected' if lang == 'en' else ''}>English</option>
                        <option value="so" {'selected' if lang == 'so' else ''}>Soomaali</option>
                    </select>
                </div>
            </div>
            <section class="hero">
                <h1>{texts['title']}</h1>
                <p>{texts['connected']}: <strong id="meter_id">Loading...</strong></p>
                <div class="status-block">Last Updated: <strong id="time">-</strong></div>
            </section>

            <div class="dashboard-grid">
                <div class="card" onclick="viewMetricDetails('voltage')">
                    <h3>{texts['voltage']}</h3>
                    <p id="voltage">0 V</p>
                </div>
                <div class="card" onclick="viewMetricDetails('current')">
                    <h3>{texts['current']}</h3>
                    <p id="current">0 A</p>
                </div>
                <div class="card" onclick="viewMetricDetails('load')">
                    <h3>{texts['load']}</h3>
                    <p id="power">0 kW</p>
                </div>
                <div class="card" onclick="viewMetricDetails('balance')">
                    <h3>{texts['balance']}</h3>
                    <p id="credit">0 kWh</p>
                </div>
            </div>

            <!-- Chart.js Analytics Card -->
            <div class=\"card\" style=\"margin-top: 20px; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);\">
                <h3 style=\"margin-top: 0; margin-bottom: 20px; color: #334155; font-size: 0.95rem; letter-spacing: 0.12em; text-transform: uppercase;\">Real-Time Voltage & Power Analytics</h3>
                <canvas id=\"iotLiveChart\" width=\"400\" height=\"150\"></canvas>
            </div>

            <!-- Live Data Grid Selectors -->
            <div class=\"card\" style=\"margin-top: 20px; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);\">
                <h3 style=\"margin-top: 0; margin-bottom: 20px; color: #334155; font-size: 0.95rem; letter-spacing: 0.12em; text-transform: uppercase;\">Live Data Grid</h3>
                <div class=\"dashboard-grid\" style=\"gap: 15px;\">
                    <div class=\"card\" style=\"box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);\">
                        <h3>LINE VOLTAGE</h3>
                        <p id=\"live-voltage-display\" style=\"font-size: 1.75rem; color: #3b82f6; font-weight: 700;\">Loading...</p>
                    </div>
                    <div class=\"card\" style=\"box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);\">
                        <h3>ACTIVE CURRENT</h3>
                        <p id=\"live-current-display\" style=\"font-size: 1.75rem; color: #3b82f6; font-weight: 700;\">Loading...</p>
                    </div>
                    <div class=\"card\" style=\"box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);\">
                        <h3>ACTIVE POWER</h3>
                        <p id=\"live-power-display\" style=\"font-size: 1.75rem; color: #3b82f6; font-weight: 700;\">Loading...</p>
                    </div>
                </div>
            </div>

            <p class=\"footer-note\">Click any card to fetch live gateway details from the backend. Chart and live data update every 3 seconds.</p>
        </div>
    </body>
    </html>
    """

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify(latest_meter_reading)

@app.route('/api/system-details')
def system_details():
    return jsonify({
        "location": "Garowe, Somalia",
        "gateway_status": "ONLINE",
        "signal_strength": "Excellent",
        "firmware_version": "v2.4.1"
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify({
        "voltage_v": latest_meter_reading.get('voltage_v', 0),
        "active_power_kw": latest_meter_reading.get('active_power_kw', 0),
        "current_a": latest_meter_reading.get('current_a', 0),
        "power_factor": latest_meter_reading.get('power_factor', 1.0),
        "remaining_credit_kwh": latest_meter_reading.get('remaining_credit_kwh', 0)
    })

@app.route('/api/meter/update', methods=['POST'])
def receive_meter_data():
    global latest_meter_reading
    incoming_payload = request.json or {}

    voltage = float(incoming_payload.get('voltage', 0))
    current = float(incoming_payload.get('current', 0))
    latest_meter_reading = {
        'meter_id': incoming_payload.get('meter_id', 'Unknown'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'voltage_v': round(voltage, 1),
        'current_a': round(current, 2),
        'active_power_kw': round((voltage * current) / 1000, 3),
        'power_factor': round(float(incoming_payload.get('power_factor', 1)), 2),
        'remaining_credit_kwh': round(float(incoming_payload.get('credit', 0)), 2),
    }
    return jsonify({'status': 'Success', 'message': 'Telemetry matrix received'}), 200

@app.route('/api/events', methods=['GET'])
def get_events():
    # Return events in FullCalendar-compatible JSON format
    return jsonify(SAMPLE_EVENTS)


@app.route('/api/events', methods=['POST'])
def create_event():
    global EVENT_COUNTER
    payload = request.json or {}
    title = payload.get('title')
    start = payload.get('start')
    end = payload.get('end')
    time = payload.get('time', '')
    if not title or not start:
        return jsonify({'error': 'Missing title or start'}), 400

    new_event = {
        'id': str(EVENT_COUNTER),
        'title': title,
        'start': start,
        'end': end,
        'time': time,
    }
    EVENT_COUNTER += 1
    SAMPLE_EVENTS.append(new_event)
    return jsonify(new_event), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
