# 🌿 EcoSnap — Smart Waste Management System

> "Snap Waste. Clean Tomorrow."

EcoSnap is a full-stack web application that allows citizens to report
waste issues in their community and track their resolution in real-time.

## 🚀 Features

- 📸 Report waste issues with photo upload
- 📍 GPS location detection
- 📊 Admin analytics dashboard
- 🔐 JWT authentication
- 📋 Real-time complaint tracking
- 🛡️ Admin panel with status management

## 🧠 Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite + SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript + Jinja2
- **Charts:** Chart.js
- **Auth:** JWT + bcrypt

## ⚡ Quick Start

### 1. Clone the repository
git clone https://github.com/YOURUSERNAME/ecosnap.git
cd ecosnap

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the app
python run.py

### 5. Open browser
http://localhost:8000

## 🔑 Default Login

| Role  | Email                | Password |
|-------|----------------------|----------|
| Admin | admin@ecosnap.com    | admin123 |

## 📁 Project Structure

ecosnap/
├── run.py
├── seed_data.py
├── requirements.txt
└── app/
    ├── main.py
    ├── auth.py
    ├── database.py
    ├── models/
    │   ├── user.py
    │   └── complaint.py
    ├── routes/
    │   ├── auth.py
    │   ├── complaints.py
    │   └── dashboard.py
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   └── ...
    ├── static/
    │   ├── css/
    │   └── js/
    └── uploads/

## 📸 Screenshots

Homepage, Login, Dashboard, Admin Panel

## 👨‍💻 Built With

FastAPI + SQLAlchemy + Jinja2 + Chart.js