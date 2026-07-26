from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.sensor_log import SensorLogCreate
from crud.crud_sensor_log import sensor_log
from core.websocket import manager

class SensorPipelineService:
    @staticmethod
    async def process_sensor_data(db: AsyncSession, simulation_id: int, raw_data: Dict[str, Any]):
        """
        Takes raw data from EnergyPlus, stores it in the database,
        and broadcasts it via WebSockets.
        """
        # Convert raw dict to Pydantic schema
        log_create = SensorLogCreate(
            simulation_id=simulation_id,
            indoor_temp=raw_data.get("indoor_temp"),
            outdoor_temp=raw_data.get("outdoor_temp"),
            humidity=raw_data.get("humidity"),
            pmv=raw_data.get("pmv"),
            hvac_energy=raw_data.get("hvac_energy"),
            cooling_energy=raw_data.get("cooling_energy"),
            heating_energy=raw_data.get("heating_energy"),
            carbon=raw_data.get("carbon"),
            occupancy=raw_data.get("occupancy")
        )

        # 1. Save to Database (best-effort — don't crash stream if DB fails)
        try:
            db_log = await sensor_log.create(db=db, obj_in=log_create)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"DB write skipped: {e}")
            # Still broadcast the raw data even if DB write fails
            await manager.broadcast_json({
                "simulation_id": simulation_id,
                "indoor_temp": raw_data.get("indoor_temp"),
                "outdoor_temp": raw_data.get("outdoor_temp"),
                "humidity": raw_data.get("humidity"),
                "pmv": raw_data.get("pmv"),
                "hvac_energy": raw_data.get("hvac_energy"),
                "cooling_energy": raw_data.get("cooling_energy"),
                "heating_energy": raw_data.get("heating_energy"),
            })
            return None

        # 2. Broadcast via WebSocket
        payload = {
            "id": db_log.id,
            "simulation_id": db_log.simulation_id,
            "timestamp": db_log.timestamp.isoformat() if db_log.timestamp else None,
            "indoor_temp": db_log.indoor_temp,
            "outdoor_temp": db_log.outdoor_temp,
            "humidity": db_log.humidity,
            "pmv": db_log.pmv,
            "hvac_energy": db_log.hvac_energy,
            "cooling_energy": db_log.cooling_energy,
            "heating_energy": db_log.heating_energy,
            "carbon": db_log.carbon,
            "occupancy": db_log.occupancy
        }
        
        await manager.broadcast_json(payload)
        return db_log
