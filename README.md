# honeywell_JayDaftardar

## Project Overview
This repository contains an autonomous, AI-driven Building Management System (BMS) powered by **EnergyPlus**, **FastAPI**, **React**, and an **Ollama-hosted Mistral LLM**. 

Instead of relying on traditional, schedule-based control systems, this platform employs a Large Language Model (LLM) to act as a dynamic decision engine. The system continuously ingests live sensor data from an EnergyPlus building simulation (using `.idf` models), reasons about current thermal conditions and energy usage, and automatically applies optimal Energy Conservation Measures (ECMs) directly back into the simulation environment. This creates a fully autonomous, closed-loop control system.

## Technical Architecture & Documentation
The project is built on a decoupled, modern software architecture. The technical design of the system is divided into the following core components:

- **Simulation Layer (EnergyPlus)**: Serves as the physical building model. The system uses the PyEnergyPlus API to step through `.idf` simulation models (`model.idf`, `model_modified.idf`), extracting sensor readings (like zone temperatures) and injecting new actuator setpoints in real-time.
- **AI Decision Engine**: A locally hosted Mistral 7B LLM (via Ollama) processes building telemetry and generates discrete control actions. It uses strict prompt engineering and deterministic validation to ensure safe building operation, evaluating the trade-offs between energy savings and thermal comfort.
- **Data Persistence (PostgreSQL)**: A normalized SQL database tracks the lifecycle of simulation runs, high-frequency sensor logs, control actions, and the raw reasoning output of the LLM for full explainability and auditing.
- **Backend Orchestration (FastAPI)**: An asynchronous REST API that coordinates the communication between the simulation, the AI agent, and the database using a strict service-layer pattern.
- **Frontend Dashboard (React)**: A modern web interface built with React, Vite, TailwindCSS, and Recharts to visualize real-time simulation metrics, energy consumption charts, and the AI's step-by-step reasoning logs.

*Note: For an in-depth breakdown of the API endpoints, database schemas, and AI validation logic, please refer to the project's generated technical documentation PDF if available in the workspace.*

---

## Local Setup

### 1. Prerequisites
- **Python 3.14** (or compatible)
- **Node.js & npm** (for the frontend dashboard)
- **PostgreSQL** running locally on port 5432
- **EnergyPlus V26.2.0** installed at `C:\EnergyPlusV26-2-0` (or update `energyplus_service.py` to match your installation path)
- **Ollama** installed on your system

### 2. Ollama & Local LLM Setup
Because this project uses a locally hosted LLM to make HVAC decisions, **no external API keys are required** and all data remains private.
1. [Download and install Ollama](https://ollama.com/download)
2. Open a terminal and pull the Mistral model:
   ```bash
   ollama pull mistral
   ```
3. Ensure the Ollama server is running (defaults to `http://localhost:11434`).

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

Run database migrations to generate the tables:
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
