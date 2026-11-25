# ThesisForge AI — Deployment & Local Setup Guide

This document provides exact instructions to deploy, run, and configure **ThesisForge AI** inside `Desktop/4vu5h/MTM606/`.

---

## 1. System Architecture & Prerequisites

- **Python Runtime:** Python 3.10+ (tested on Python 3.13)
- **Database:** SQLite (default at `web-app/storage/thesisforge.db`) or PostgreSQL with connection string
- **Core Dependencies:** `fastapi`, `uvicorn`, `pydantic`, `semantic-kernel`, `pypdf`, `pytest`

---

## 2. Local Setup & Quickstart

### Step 1: Navigate to Project Directory
```powershell
cd C:\Users\91860\Desktop\4vu5h\MTM606
```

### Step 2: Install Dependencies (if not already installed)
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Web Application
You can run it in either of two ways:

**Option A: One-click Batch File**
Double-click `Start ThesisForge.bat` or run in terminal:
```powershell
.\Start ThesisForge.bat
```

**Option B: Python Launcher**
```powershell
python run_app.py
```

**Option C: From inside `web-app/`**
```powershell
cd web-app
python run_app.py
```

- **Web Application UI:** `http://localhost:8000`
- **Interactive API Documentation (Swagger):** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`

---

## 3. Running Automated Tests

Run the complete 20-test automated suite (including API, RAG, scenarios, anti-fabrication, and stock universe):
```powershell
cd C:\Users\91860\Desktop\4vu5h\MTM606
pytest -v
```

---

## 4. Running the Demo Notebook

Open the pre-executed Jupyter notebook:
```powershell
cd C:\Users\91860\Desktop\4vu5h\MTM606
jupyter notebook notebooks/thesisforge_demo.ipynb
```

---

## 5. Docker Deployment

```powershell
cd C:\Users\91860\Desktop\4vu5h\MTM606
docker-compose up --build -d
```
Verify the container health:
```powershell
curl http://localhost:8000/health
```
