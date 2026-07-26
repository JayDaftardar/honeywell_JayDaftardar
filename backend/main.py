from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.sensors import router as sensors_router
from api.simulation import router as simulation_router
from api.agent import router as agent_router
from api.analytics import router as analytics_router

app.include_router(sensors_router, prefix="/sensor", tags=["Sensors"])
app.include_router(simulation_router, prefix="/simulation", tags=["Simulation"])
app.include_router(agent_router, prefix="/agent", tags=["AI Agent"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Building AI API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
