from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="running")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor_logs = relationship("SensorLog", back_populates="simulation", cascade="all, delete-orphan")
    control_actions = relationship("ControlAction", back_populates="simulation", cascade="all, delete-orphan")
    ai_decisions = relationship("AIDecision", back_populates="simulation", cascade="all, delete-orphan")
