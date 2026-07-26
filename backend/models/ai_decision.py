from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class AIDecision(Base):
    __tablename__ = "ai_decisions"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    action = Column(String, nullable=True)
    setpoint = Column(Float, nullable=True)
    fan_speed = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    simulation = relationship("Simulation", back_populates="ai_decisions")
