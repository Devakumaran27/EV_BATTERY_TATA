# EV Battery Thermal Monitor 🚗🔋

## Overview  
EV Battery Thermal Monitor is a full-stack web application built to **track and visualize thermal and voltage data of an electric vehicle’s battery pack in real time**. It helps monitor battery health, detect thermal anomalies, and send alerts when critical thresholds are exceeded — aiming to improve safety, reliability, and performance of EV systems.

## 🔎 Motivation & Purpose  
High-performance EV batteries (especially Li-ion packs) are sensitive to temperature. Overheating can degrade performance, reduce lifespan, or even cause thermal runaway.  
This project was created to:  
- Provide an easy-to-use dashboard for monitoring battery temperature and voltage.  
- Enable real-time data logging and alerts for safety.  
- Serve as a prototype / reference for EV battery thermal management and research projects.

## 📦 Tech Stack & Architecture  

| Layer | Technologies / Tools |
|-------|---------------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python (Flask) |
| Database | MySQL |
| Data Flow | Sensors → Data stream → Flask API → MySQL → Web Dashboard |
| Deployment | (Your server/hosting info — to be filled) |

## ⚙️ Features  

- ✅ Real-time reception of battery sensor data (temperature, voltage, etc.)  
- 📊 Interactive dashboard with charts/graphs & status indicators for battery parameters  
- 🔔 Automatic alert generation when temperature or voltage exceeds predefined safe thresholds  
- 📥 Historical logging: all received data is stored in MySQL for later review/analysis  
- 🔧 Modular architecture: easy to extend (e.g. add more sensor types, analytics, log export)  

## 🚀 Getting Started  

### Prerequisites  
- Python 3.x  
- MySQL (or compatible) database server  
- Web browser (for dashboard)  
- (Optional) Sensor setup hardware & interface to feed data  

### Installation & Setup  
1. Clone the repository  
   git clone https://github.com/Devakumaran27/EV_BATTERY_TATA.git
   
2. Navigate to backend folder and install dependencies
cd EV_BATTERY_TATA/backend  
pip install -r requirements.txt  

3. Configure database connection in the backend (e.g. in config.py or .env)
DB_HOST=...
DB_USER=...
DB_PASS=...
DB_NAME=...
4. Migrate / initialize the database (if required) / create tables

5. Run the Flask backend
python app.py

-Usage
-Once backend is running and sensors are streaming data, the dashboard will automatically display real-time battery parameters.
-Watch the status indicators: if battery temperature or voltage crosses safe thresholds — receive visual alert/warning on dashboard.

You can browse historical data from MySQL for analysis or export.

-🛠️ (Optional) Extend / Customize
You can extend this project by:
-Adding support for more sensors (current, state-of-charge, cell-level temp, etc.)
-Implementing user authentication for secure access
-Adding email/SMS notifications on critical alerts
-Exporting data or generating reports (CSV, graphs, analytics)

=Project Structure (at a glance)
EV_BATTERY_TATA/
│
├── backend/       # Flask server, API endpoints, DB configs  
├── frontend/      # HTML / CSS / JS dashboard UI  
├── .gitattributes
└── README.md      # ← this file  
Next Steps / To-Do / Future Work

 =Secure deployment on cloud / remote server for real-time access
 -Add advanced analytics & visualizations (e.g. trend graphs, averages, battery-health metrics)
 -Add alert notifications (email / SMS)
 -Add documentation for sensor wiring / hardware interface
 -Write test scripts / validation module

-👤 Author
Developed by Devakumaran27
GitHub: https://github.com/Devakumaran27
