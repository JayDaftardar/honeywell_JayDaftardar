from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class SimulationBase(BaseModel):
    status: Optional[str] = "running"
    end_time: Optional[datetime] = None

class SimulationCreate(SimulationBase):
    pass

class SimulationUpdate(SimulationBase):
    pass

class SimulationInDBBase(SimulationBase):
    id: int
    start_time: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Simulation(SimulationInDBBase):
    pass
