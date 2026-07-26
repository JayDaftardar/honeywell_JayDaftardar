# Smart Building AI

This is a local, autonomous Building Management System (BMS) powered by EnergyPlus, FastAPI, and an Ollama-hosted Mistral LLM.

## Local Setup

### 1. Prerequisites
- **Python 3.14** (or compatible)
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
