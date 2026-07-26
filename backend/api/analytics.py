from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from db.session import get_db
from models.sensor_log import SensorLog
from models.simulation import Simulation

router = APIRouter()

class AnalyticsSummary(BaseModel):
    baseline_energy_kwh: float
    ai_energy_kwh: float
    energy_saved_kwh: float
    cost_saved_usd: float
    carbon_reduced_kg: float
    savings_percentage: float
    baseline_avg_watts: float
    ai_avg_watts: float
    baseline_steps: int
    ai_steps: int

async def _get_sim_id(db, mode: str, explicit_id: Optional[int]) -> Optional[int]:
    """Return the simulation ID to use (explicit or latest of that mode)."""
    if explicit_id:
        return explicit_id
    q = select(Simulation.id).where(Simulation.mode == mode).order_by(Simulation.id.desc()).limit(1)
    res = await db.execute(q)
    return res.scalar()

async def _get_avg_and_count(db, sim_id: Optional[int]):
    """Return (avg_hvac_watts, step_count) for the given simulation_id."""
    if sim_id is None:
        return 0.0, 0
    avg_q = select(func.avg(SensorLog.hvac_energy), func.count(SensorLog.id)).where(
        SensorLog.simulation_id == sim_id
    )
    res = await db.execute(avg_q)
    row = res.one()
    avg_w = float(row[0] or 0.0)
    count = int(row[1] or 0)
    return avg_w, count


@router.get("/comparison", response_model=AnalyticsSummary)
async def get_comparison(
    baseline_id: int = None,
    ai_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns analytics comparing a baseline simulation to an AI simulation.
    Uses AVERAGE watts (normalized) so run-length differences don't skew results.
    Energy is expressed as equivalent kWh over a standard 8-hour operational day.
    """
    latest_ai_id = await _get_sim_id(db, "ai", ai_id)
    latest_baseline_id = await _get_sim_id(db, "baseline", baseline_id)

    ai_avg_w, ai_steps = await _get_avg_and_count(db, latest_ai_id)
    baseline_avg_w, baseline_steps = await _get_avg_and_count(db, latest_baseline_id)

    if baseline_avg_w == 0.0 or ai_avg_w == 0.0 or baseline_steps == 0 or ai_steps == 0:
        raise HTTPException(
            status_code=400,
            detail="Missing baseline or AI simulation data. Please run both a Baseline and an AI simulation first."
        )

    # Scale average watts to an equivalent 8-hour operational day in kWh
    # kWh = avg_watts * hours / 1000
    # This gives a real-world comparable number regardless of demo run duration.
    HOURS_PER_DAY = 8.0
    baseline_energy_kwh = baseline_avg_w * HOURS_PER_DAY / 1000.0
    ai_energy_kwh = ai_avg_w * HOURS_PER_DAY / 1000.0

    energy_saved_kwh = baseline_energy_kwh - ai_energy_kwh

    # Cost: $0.15 per kWh (US commercial average)
    cost_saved_usd = energy_saved_kwh * 0.15
    # Carbon: 0.386 kg CO2 per kWh (US grid average, EPA 2023)
    carbon_reduced_kg = energy_saved_kwh * 0.386

    savings_percentage = 0.0
    if baseline_energy_kwh > 0:
        savings_percentage = (energy_saved_kwh / baseline_energy_kwh) * 100

    return AnalyticsSummary(
        baseline_energy_kwh=round(baseline_energy_kwh, 2),
        ai_energy_kwh=round(ai_energy_kwh, 2),
        energy_saved_kwh=round(energy_saved_kwh, 2),
        cost_saved_usd=round(cost_saved_usd, 2),
        carbon_reduced_kg=round(carbon_reduced_kg, 2),
        savings_percentage=round(savings_percentage, 1),
        baseline_avg_watts=round(baseline_avg_w, 1),
        ai_avg_watts=round(ai_avg_w, 1),
        baseline_steps=baseline_steps,
        ai_steps=ai_steps,
    )

