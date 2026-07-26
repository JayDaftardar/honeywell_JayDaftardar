import asyncio
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from services.energyplus_service import EnergyPlusService
from services.sensor_pipeline import SensorPipelineService
from services.decision_engine import decision_engine
from services.llm_agent import llm_agent
from crud.crud_simulation import simulation as crud_simulation
from schemas.simulation import SimulationCreate, SimulationUpdate

logger = logging.getLogger(__name__)


class SimulationRunner:
    """
    Manages the lifecycle of a single EnergyPlus simulation run.
    Drives the step-by-step loop, collects sensor data via the
    SensorPipelineService, and exposes controls to the API layer.
    """

    def __init__(self):
        self._eplus: Optional[EnergyPlusService] = None
        self._running = False
        self._paused = False
        self._task: Optional[asyncio.Task] = None
        self._simulation_id: Optional[int] = None
        self._idf_path: str = "model.idf"
        self._epw_path: str = "weather.epw"
        self._mode: str = "ai"

    # ------------------------------------------------------------------ #
    # Public state                                                         #
    # ------------------------------------------------------------------ #
    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def simulation_id(self) -> Optional[int]:
        return self._simulation_id

    def get_status(self) -> Dict[str, Any]:
        return {
            "simulation_id": self._simulation_id,
            "running": self._running,
            "paused": self._paused,
            "idf_path": self._idf_path,
            "epw_path": self._epw_path,
            "mode": self._mode,
        }

    # ------------------------------------------------------------------ #
    # Control                                                              #
    # ------------------------------------------------------------------ #
    async def start(
        self,
        db: AsyncSession,
        idf_path: str = "model.idf",
        epw_path: str = "weather.epw",
        mode: str = "ai"
    ) -> int:
        """Start a new simulation and return its database ID."""
        if self._running:
            raise RuntimeError("A simulation is already running.")

        self._idf_path = idf_path
        self._epw_path = epw_path
        self._mode = mode

        # Create a Simulation record in the DB
        db_sim = await crud_simulation.create(
            db=db, obj_in=SimulationCreate(status="running")
        )
        await db.commit()
        await db.refresh(db_sim)
        self._simulation_id = db_sim.id

        # Boot up EnergyPlusService
        self._eplus = EnergyPlusService()
        self._running = True
        self._paused = False

        # Kick off the background coroutine loop
        self._task = asyncio.create_task(
            self._run_loop(db, idf_path, epw_path, mode)
        )
        logger.info(f"SimulationRunner started (simulation_id={self._simulation_id})")
        return self._simulation_id

    def pause(self):
        """Pause after the current timestep completes."""
        if not self._running:
            raise RuntimeError("No simulation is currently running.")
        self._paused = True
        if self._eplus:
            self._eplus.pause()
        logger.info("SimulationRunner paused.")

    def resume(self):
        """Resume a paused simulation."""
        if not self._running:
            raise RuntimeError("No simulation is currently running.")
        self._paused = False
        if self._eplus:
            self._eplus.resume()
        logger.info("SimulationRunner resumed.")

    async def stop(self, db: AsyncSession):
        """Stop the simulation and mark it finished in the DB."""
        if not self._running:
            raise RuntimeError("No simulation is currently running.")
        self._running = False
        if self._eplus:
            self._eplus.stop()
        if self._task:
            self._task.cancel()

        # Mark the simulation as stopped in the DB
        if self._simulation_id:
            from datetime import datetime
            await crud_simulation.update(
                db=db,
                db_obj=await crud_simulation.get(db, id=self._simulation_id),
                obj_in=SimulationUpdate(status="stopped", end_time=datetime.utcnow()),
            )
            await db.commit()

        logger.info(f"SimulationRunner stopped (simulation_id={self._simulation_id})")
        self._simulation_id = None
        self._eplus = None

    # ------------------------------------------------------------------ #
    # Internal loop                                                        #
    # ------------------------------------------------------------------ #
    async def _run_loop(self, db: AsyncSession, idf_path: str, epw_path: str, mode: str):
        """
        Background loop: advances the simulation one timestep at a time,
        feeds data into the Sensor Pipeline, then yields to the event loop.
        A placeholder hook for AI decisions is included here (Module 6+).
        """
        # Start the EnergyPlus simulation in its own background thread
        self._eplus.start(idf_path=idf_path, epw_path=epw_path)

        try:
            while self._running:
                if not self._eplus or not self._eplus._running:
                    # Simulation thread finished — wait a moment and exit
                    await asyncio.sleep(0.5)
                    break
                if not self._paused:
                    # Step the simulation forward by one timestep
                    sensor_data = await self._eplus.step()

                    if sensor_data:
                        # Persist & broadcast via the Sensor Pipeline
                        await SensorPipelineService.process_sensor_data(
                            db=db,
                            simulation_id=self._simulation_id,
                            raw_data=sensor_data,
                        )

                        if mode == "ai":
                            # --- Module 6/7: Ask LLM for a decision and process via Decision Engine ---
                            decision = await llm_agent.decide(sensor_data)
                            if decision:
                                # Process the decision through the decision engine
                                control_action = await decision_engine.process_decision(
                                    db=db,
                                    simulation_id=self._simulation_id,
                                    raw_decision=decision,
                                    eplus_service=self._eplus
                                )
                                
                                if control_action:
                                    # Broadcast the AI decision and control action via WebSocket
                                    from core.websocket import manager
                                    await manager.broadcast_json({
                                        "type": "ai_decision",
                                        "action": decision.action,
                                        "setpoint": decision.setpoint,
                                        "fan_speed": decision.fan_speed,
                                        "reasoning": decision.reasoning,
                                        "confidence": decision.confidence,
                                        "applied_setpoint": control_action.setpoint,
                                        "applied_fan_speed": control_action.fan_speed,
                                        "action_applied": control_action.applied
                                    })
                            # ------------------------------------------------

                # Yield to event loop between steps; keeps the server responsive
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("SimulationRunner loop cancelled.")
        except Exception as e:
            logger.error(f"Unexpected error in simulation loop: {e}", exc_info=True)
        finally:
            self._running = False
            logger.info("SimulationRunner loop exited.")


# Module-level singleton — shared across the FastAPI application
runner = SimulationRunner()
