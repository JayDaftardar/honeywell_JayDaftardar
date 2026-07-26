from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class SensorLog(Base):
    __tablename__ = "sensor_logs"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    indoor_temp = Column(Float, nullable=True)
    outdoor_temp = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pmv = Column(Float, nullable=True)
    hvac_energy = Column(Float, nullable=True)
    cooling_energy = Column(Float, nullable=True)
    heating_energy = Column(Float, nullable=True)
    carbon = Column(Float, nullable=True)
    occupancy = Column(Float, nullable=True)

    simulation = relationship("Simulation", back_populates="sensor_logs")
