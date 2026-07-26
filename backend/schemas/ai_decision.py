from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AIDecisionBase(BaseModel):
    action: Optional[str] = None
    setpoint: Optional[float] = None
    fan_speed: Optional[float] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None

class AIDecisionCreate(AIDecisionBase):
    simulation_id: int

class AIDecisionUpdate(AIDecisionBase):
    pass

class AIDecisionInDBBase(AIDecisionBase):
    id: int
    simulation_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class AIDecision(AIDecisionInDBBase):
    pass
