from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class ControlAction(Base):
    __tablename__ = "control_actions"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    setpoint = Column(Float, nullable=True)
    fan_speed = Column(Float, nullable=True)
    applied = Column(Boolean, default=False)

    simulation = relationship("Simulation", back_populates="control_actions")
