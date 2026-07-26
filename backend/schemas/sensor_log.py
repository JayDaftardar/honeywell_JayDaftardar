from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class SensorLogBase(BaseModel):
    indoor_temp: Optional[float] = None
    outdoor_temp: Optional[float] = None
    humidity: Optional[float] = None
    pmv: Optional[float] = None
    hvac_energy: Optional[float] = None
    cooling_energy: Optional[float] = None
    heating_energy: Optional[float] = None
    carbon: Optional[float] = None
    occupancy: Optional[float] = None

class SensorLogCreate(SensorLogBase):
    simulation_id: int

class SensorLogUpdate(SensorLogBase):
    pass

class SensorLogInDBBase(SensorLogBase):
    id: int
    simulation_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class SensorLog(SensorLogInDBBase):
    pass
