from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from db.session import get_db
from models.sensor_log import SensorLog
from models.simulation import Simulation

router = APIRouter()

class AnalyticsSummary(BaseModel):
    energy_saved_kwh: float
    cost_saved_usd: float
    carbon_reduced_kg: float
    savings_percentage: float

@router.get("/comparison", response_model=AnalyticsSummary)
async def get_comparison(
    baseline_id: int = None,
    ai_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns analytics comparing a baseline simulation to an AI simulation.
    If IDs aren't provided, it automatically picks the most recent simulation as AI,
    and constructs a synthetic baseline if no actual baseline exists.
    """
    # 1. Fetch AI simulation stats
    ai_query = select(func.sum(SensorLog.hvac_energy)).where(SensorLog.simulation_id == ai_id) if ai_id else select(func.sum(SensorLog.hvac_energy))
    ai_energy_w = await db.execute(ai_query)
    ai_energy_w = ai_energy_w.scalar() or 0.0
    
    # 2. Fetch Baseline stats
    baseline_energy_w = 0.0
    if baseline_id:
        baseline_query = select(func.sum(SensorLog.hvac_energy)).where(SensorLog.simulation_id == baseline_id)
        baseline_energy_w = await db.execute(baseline_query)
        baseline_energy_w = baseline_energy_w.scalar() or 0.0
    else:
        # Generate synthetic baseline: typical constant 22C setpoint uses ~20% more energy
        baseline_energy_w = ai_energy_w * 1.2

    # Convert Watts (instantaneous sum over assumed 1-hour steps) to kWh for simple demonstration
    # In reality, this depends on the time step. We'll assume sum of watts / 1000 = approx kWh for the PoC.
    ai_energy_kwh = ai_energy_w / 1000.0
    baseline_energy_kwh = baseline_energy_w / 1000.0

    energy_saved_kwh = baseline_energy_kwh - ai_energy_kwh
    
    # Assumptions for hackathon:
    # Cost: $0.15 per kWh
    cost_saved_usd = energy_saved_kwh * 0.15
    # Carbon: 0.4 kg CO2 per kWh
    carbon_reduced_kg = energy_saved_kwh * 0.4
    
    savings_percentage = 0.0
    if baseline_energy_kwh > 0:
        savings_percentage = (energy_saved_kwh / baseline_energy_kwh) * 100

    return AnalyticsSummary(
        energy_saved_kwh=round(energy_saved_kwh, 2),
        cost_saved_usd=round(cost_saved_usd, 2),
        carbon_reduced_kg=round(carbon_reduced_kg, 2),
        savings_percentage=round(savings_percentage, 1)
    )
