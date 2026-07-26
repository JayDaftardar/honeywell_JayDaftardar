from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ControlActionBase(BaseModel):
    setpoint: Optional[float] = None
    fan_speed: Optional[float] = None
    applied: Optional[bool] = False

class ControlActionCreate(ControlActionBase):
    simulation_id: int

class ControlActionUpdate(ControlActionBase):
    pass

class ControlActionInDBBase(ControlActionBase):
    id: int
    simulation_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ControlAction(ControlActionInDBBase):
    pass
