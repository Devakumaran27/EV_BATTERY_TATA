import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Allow frontend to communicate

# Config
DATABASE = 'database.db'
PDF_FOLDER = 'static/export_pdf'
os.makedirs(PDF_FOLDER, exist_ok=True)

# Initialize Database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Vehicle Registration Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                serial_number TEXT PRIMARY KEY,
                car_name TEXT,
                battery_model TEXT,
                battery_capacity REAL,
                manufacturer TEXT,
                commissioning_date TEXT,
                other_info TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Sensor Data Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                voltage REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Alert History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Helper: Get DB connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# --- API ROUTES ---

# 1. Register Vehicle
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO vehicles 
            (serial_number, car_name, battery_model, battery_capacity, manufacturer, commissioning_date, other_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['serialNumber'],
            data['carName'],
            data['batteryModel'],
            data['batteryCapacity'],
            data['manufacturer'],
            data['commissioningDate'],
            data.get('otherInfo', '{}')
        ))
        conn.commit()
        return jsonify({"message": "Vehicle registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 2. Fetch Real-time Data (latest sensor + vehicle if available)
@app.route('/data')
def get_data():
    try:
        conn = get_db()
        # Get latest sensor data
        sensor = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1').fetchone()
        # Get vehicle info (if serial is known)
        vehicle = conn.execute('SELECT * FROM vehicles LIMIT 1').fetchone()  # Simplified: assume one vehicle

        return jsonify({
            "temperature": sensor['temperature'] if sensor else 25.0,
            "voltage": sensor['voltage'] if sensor else 380.0,
            "vehicle_info": dict(vehicle) if vehicle else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Simulate Sensor Data (for demo) — Remove in production
@app.route('/simulate')
def simulate_data():
    from random import uniform
    temp = round(uniform(30, 60), 2)
    volt = round(uniform(350, 400), 2)

    with get_db() as conn:
        conn.execute('INSERT INTO sensor_data (temperature, voltage) VALUES (?, ?)', (temp, volt))
        if temp > 50:
            conn.execute('INSERT INTO alerts (temperature, details) VALUES (?, ?)',
                         (temp, f'High temperature alert: {temp}°C'))
        conn.commit()

    return jsonify({"temperature": temp, "voltage": volt})

# 4. Fetch Alert History
@app.route('/history')
def history():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50').fetchall()
        alerts = [dict(row) for row in rows]
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. Export PDF Certificate
from jinja2 import Template

@app.route('/export_pdf/<serial_number>')
def export_pdf(serial_number):
    try:
        conn = get_db()
        vehicle = conn.execute('SELECT * FROM vehicles WHERE serial_number = ?', (serial_number,)).fetchone()
        sensor = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1').fetchone()

        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        # Render HTML template for PDF
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Battery Risk Certificate</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: white; }
                .header { text-align: center; margin-bottom: 30px; }
                .title { color: #4338ca; font-size: 32px; font-weight: bold; margin-bottom: 10px; }
                .subtitle { color: #6b7280; font-size: 16px; }
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
                .card { background: #f9fafb; padding: 15px; border-radius: 8px; }
                .risk-high { background: #dc2626; color: white; padding: 5px 10px; border-radius: 20px; }
                .risk-elevated { background: #d97706; color: white; padding: 5px 10px; border-radius: 20px; }
                .risk-normal { background: #059669; color: white; padding: 5px 10px; border-radius: 20px; }
                .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 40px; }
                @media print { body { margin: 20px; } }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🔋 EV Battery Risk Certificate</div>
                <div class="subtitle">Official Health Assessment Report</div>
                <hr style="margin: 20px 0; border: 1px solid #d1d5db;">
            </div>
            <div class="grid">
                <div class="card"><strong>Car Name:</strong> {{ car_name }}</div>
                <div class="card"><strong>Battery Model:</strong> {{ battery_model }}</div>
                <div class="card"><strong>Serial Number:</strong> {{ serial_number }}</div>
                <div class="card"><strong>Capacity:</strong> {{ battery_capacity }} kWh</div>
                <div class="card"><strong>Temperature:</strong> {{ temperature }} °C</div>
                <div class="card">
                    <strong>Status:</strong> 
                    <span class="risk-{{ temp_risk.lower() }}">{{ temp_risk }} Risk</span>
                </div>
            </div>
            <div style="margin-bottom: 30px;">
                <h3 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Assessment Summary</h3>
                <p>{{ summary }}</p>
            </div>
            <div class="footer">
                Generated on: {{ timestamp }} | EV Battery Health Platform
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        
        # Handle case where sensor data is None
        if sensor is None:
            temp_risk = "Normal"
            summary = "No sensor data available. Battery condition assessment pending."
        else:
            temp_risk = "High" if sensor['temperature'] > 50 else "Elevated" if sensor['temperature'] > 45 else "Normal"
            summary = (
                "CRITICAL: Immediate cooling recommended." if temp_risk == "High" else
                "Elevated temperature. Avoid fast charging." if temp_risk == "Elevated" else
                "Battery condition is stable and within safe limits."
            )

        html_out = template.render(
            car_name=vehicle['car_name'],
            battery_model=vehicle['battery_model'],
            serial_number=vehicle['serial_number'],
            battery_capacity=vehicle['battery_capacity'],
            temperature=sensor['temperature'] if sensor else 'N/A',
            temp_risk=temp_risk,
            summary=summary,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Return HTML that can be printed as PDF
        return html_out, 200, {'Content-Type': 'text/html'}

    except Exception as e:
        print("PDF Error:", str(e))
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

# 6. Serve Frontend (Optional: for testing)
@app.route('/')
def index():
    return send_from_directory('../frontend', 'frontend.html')

# Add this to simulate real-time updates
from threading import Thread
import time

def auto_simulate():
    while True:
        with app.test_client() as c:
            c.get('/simulate')
        time.sleep(10)  # Every 10 seconds

# Uncomment below to auto-simulate
# Thread(target=auto_simulate, daemon=True).start()

# --- Run App ---
if __name__ == '__main__':
    init_db()
    print("💡 Visit http://localhost:5000 to access the dashboard")
    app.run(host='0.0.0.0', port=5000, debug=True)