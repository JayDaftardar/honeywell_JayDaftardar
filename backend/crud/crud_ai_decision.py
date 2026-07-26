from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud.base import CRUDBase
from models.ai_decision import AIDecision
from schemas.ai_decision import AIDecisionCreate, AIDecisionUpdate

class CRUDAIDecision(CRUDBase[AIDecision, AIDecisionCreate, AIDecisionUpdate]):
    async def get_by_simulation(self, db: AsyncSession, *, simulation_id: int, skip: int = 0, limit: int = 100) -> List[AIDecision]:
        result = await db.execute(select(self.model).filter(self.model.simulation_id == simulation_id).offset(skip).limit(limit))
        return result.scalars().all()

ai_decision = CRUDAIDecision(AIDecision)
