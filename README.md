# Smart Building AI

This is a local, autonomous Building Management System (BMS) powered by **EnergyPlus**, **FastAPI**, **React**, and an **Ollama-hosted Mistral LLM**. 

Instead of traditional rule-based schedules, an LLM observes the building state, reasons over live sensor values, decides optimal Energy Conservation Measures (ECMs), and automatically applies those changes back into the EnergyPlus simulation. This forms a fully autonomous closed-loop control system.

---

## Features
- **Autonomous Decision Making**: The system evaluates live data and outputs optimal setpoint adjustments.
- **Closed-Loop Control**: Changes are applied directly back to the EnergyPlus simulation in real time.
- **Explainable AI Reasoning**: All LLM decisions and contexts are logged in the database for auditing and transparency.
- **Local & Private**: No external API keys are required. The entire LLM inference runs locally via Ollama.
- **Modern Tech Stack**: Built with React, FastAPI, SQLAlchemy, and PostgreSQL.

---

## Local Setup

### 1. Prerequisites
- **Python 3.14** (or compatible)
- **Node.js & npm** (for frontend)
- **PostgreSQL** running locally on port 5432
- **EnergyPlus V26.2.0** installed at `C:\EnergyPlusV26-2-0` (or update `energyplus_service.py`)
- **Ollama** installed on your system

### 2. Ollama & Local LLM Setup
This project uses a locally hosted LLM to make HVAC decisions, meaning **no external API keys are required**.

1. [Download and install Ollama](https://ollama.com/download)
2. Open a terminal and pull the Mistral 7B model:
   ```bash
   ollama pull mistral
   ```
3. Ensure the Ollama server is running (usually runs automatically after installation at `http://localhost:11434`).

### 3. Backend Setup
Create your virtual environment and install dependencies:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Set up your `.env` file in the `backend/` directory:
```
DATABASE_URL=postgresql+asyncpg://postgres:<your_password>@localhost:5432/smartbuilding
```
*(The Ollama base URL and model name will default to `http://localhost:11434/v1` and `mistral` respectively).*

Run database migrations:
```bash
alembic upgrade head
```

### 4. Running the Application
Start the FastAPI backend:
```bash
cd backend
.\venv\Scripts\uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

Start the React frontend (in a separate terminal):
```bash
cd frontend
npm install
npm run dev
```

---

## Technical Documentation
For an in-depth look into the project's architecture, database schema, AI decision engine, and API endpoints, please refer to the [Technical_Documentation.pdf](./Technical_Documentation.pdf) included in the root directory.
