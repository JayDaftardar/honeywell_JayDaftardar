from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud.base import CRUDBase
from models.sensor_log import SensorLog
from schemas.sensor_log import SensorLogCreate, SensorLogUpdate

class CRUDSensorLog(CRUDBase[SensorLog, SensorLogCreate, SensorLogUpdate]):
    async def get_by_simulation(self, db: AsyncSession, *, simulation_id: int, skip: int = 0, limit: int = 100) -> List[SensorLog]:
        result = await db.execute(select(self.model).filter(self.model.simulation_id == simulation_id).offset(skip).limit(limit))
        return result.scalars().all()

sensor_log = CRUDSensorLog(SensorLog)
