from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.session import get_db
from services.simulation_runner import runner
from crud.crud_simulation import simulation as crud_simulation
from schemas.simulation import Simulation, SimulationCreate

router = APIRouter()


@router.post("/start", response_model=dict)
async def start_simulation(
    idf_path: str = "model.idf",
    epw_path: str = "USA_CO_Golden-NREL.724666_TMY3.epw",
    mode: str = "ai",
    db: AsyncSession = Depends(get_db),
):
    """Start a new EnergyPlus simulation."""
    if runner.is_running:
        raise HTTPException(status_code=409, detail="A simulation is already running.")
    try:
        simulation_id = await runner.start(db=db, idf_path=idf_path, epw_path=epw_path, mode=mode)
        return {"message": "Simulation started.", "simulation_id": simulation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause", response_model=dict)
async def pause_simulation():
    """Pause the running simulation."""
    if not runner.is_running:
        raise HTTPException(status_code=409, detail="No simulation is currently running.")
    runner.pause()
    return {"message": "Simulation paused."}


@router.post("/resume", response_model=dict)
async def resume_simulation():
    """Resume a paused simulation."""
    if not runner.is_running:
        raise HTTPException(status_code=409, detail="No simulation is currently running.")
    runner.resume()
    return {"message": "Simulation resumed."}

@router.post("/step", response_model=dict)
async def step_simulation():
    """Run one step of a paused simulation."""
    if not runner.is_running:
        raise HTTPException(status_code=409, detail="No simulation is currently running.")
    
    # We could implement a one-step logic in the runner. Currently not fully exposed
    # but we can resume and pause very quickly, or actually call the EnergyPlusService step event.
    # The simplest way if it's paused is to set the step_event once.
    if runner._eplus:
        runner._eplus._step_event.set()
        return {"message": "Simulation advanced by one step."}
    return {"message": "No active simulation backend."}


@router.post("/stop", response_model=dict)
async def stop_simulation(db: AsyncSession = Depends(get_db)):
    """Stop the running simulation."""
    if not runner.is_running:
        raise HTTPException(status_code=409, detail="No simulation is currently running.")
    try:
        await runner.stop(db=db)
        return {"message": "Simulation stopped."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=dict)
async def get_simulation_status():
    """Get the current status of the simulation runner."""
    return runner.get_status()


@router.get("/history", response_model=List[Simulation])
async def get_simulation_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all historical simulation records."""
    return await crud_simulation.get_multi(db, skip=skip, limit=limit)


@router.post("/export-modified-idf", response_model=dict)
async def export_modified_idf(simulation_id: int = None):
    """
    Generates model_modified.idf by reading AI decisions from the database and
    patching the baseline IDF with the AI's average optimal setpoints.
    Satisfies Hackathon Deliverable #2: Modified IDF generated during runtime evaluation.
    """
    from generate_modified_idf import generate_modified_idf
    result = await generate_modified_idf(simulation_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
