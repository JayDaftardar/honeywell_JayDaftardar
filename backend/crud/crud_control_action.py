from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud.base import CRUDBase
from models.control_action import ControlAction
from schemas.control_action import ControlActionCreate, ControlActionUpdate

class CRUDControlAction(CRUDBase[ControlAction, ControlActionCreate, ControlActionUpdate]):
    async def get_by_simulation(self, db: AsyncSession, *, simulation_id: int, skip: int = 0, limit: int = 100) -> List[ControlAction]:
        result = await db.execute(select(self.model).filter(self.model.simulation_id == simulation_id).offset(skip).limit(limit))
        return result.scalars().all()

control_action = CRUDControlAction(ControlAction)
