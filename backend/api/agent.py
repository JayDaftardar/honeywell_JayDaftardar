from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.llm_agent import llm_agent
from services.energyplus_service import EnergyPlusService

router = APIRouter()

_last_eplus: EnergyPlusService | None = None  # shared reference for on-demand calls


@router.post("/decide", response_model=dict)
async def ai_decide(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger the Mistral agent with the latest sensor data
    from the currently running simulation. Useful for testing.
    """
    from services.simulation_runner import runner

    if not runner.is_running:
        raise HTTPException(status_code=409, detail="No simulation is running. Start one first.")

    sensor_data = runner._eplus.current_sensor_values if runner._eplus else {}
    if not sensor_data:
        raise HTTPException(status_code=404, detail="No sensor data available yet.")

    decision = await llm_agent.decide(sensor_data)
    if decision is None:
        raise HTTPException(status_code=502, detail="LLM agent returned no decision.")

    return {
        "action": decision.action,
        "setpoint": decision.setpoint,
        "fan_speed": decision.fan_speed,
        "reasoning": decision.reasoning,
        "confidence": decision.confidence,
        "sensor_snapshot": sensor_data,
    }
