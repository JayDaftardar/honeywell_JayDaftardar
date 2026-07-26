import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from services.llm_agent import AIDecision as LLMAIDecision
from schemas.ai_decision import AIDecisionCreate
from schemas.control_action import ControlActionCreate, ControlAction
from crud.crud_ai_decision import ai_decision as crud_ai_decision
from crud.crud_control_action import control_action as crud_control_action
from services.energyplus_service import EnergyPlusService

logger = logging.getLogger(__name__)

class DecisionEngineService:
    """
    Validates, sanitizes, and persists decisions from the AI.
    Acts as a safety guardrail between the LLM and physical systems.
    """
    
    # Safety Limits — must stay within safe HVAC operating range
    # MIN 23°C: HTGSETP_SCH is 21°C during occupancy; EnergyPlus requires
    # cooling setpoint > heating setpoint + ~1°C deadband to avoid fatal error:
    # "DualSetPointWithDeadBand: heating set-point higher than cooling set-point"
    MIN_SETPOINT = 23.0
    MAX_SETPOINT = 26.0
    MIN_FAN_SPEED = 0.0
    MAX_FAN_SPEED = 100.0
    MIN_CONFIDENCE = 0.5
    VALID_ACTIONS = {"reduce_setpoint", "increase_setpoint", "increase_fan_speed", "reduce_fan_speed", "hold"}

    async def process_decision(
        self, 
        db: AsyncSession, 
        simulation_id: int, 
        raw_decision: LLMAIDecision,
        eplus_service: Optional[EnergyPlusService] = None
    ) -> Optional[ControlAction]:
        """
        Takes a raw decision from the LLM, logs it, sanitizes it, 
        saves a safe control action, and optionally applies it.
        """
        
        # 1. Log the raw AI decision exactly as the LLM provided it
        ai_decision_data = AIDecisionCreate(
            simulation_id=simulation_id,
            action=raw_decision.action,
            setpoint=raw_decision.setpoint,
            fan_speed=raw_decision.fan_speed,
            reasoning=raw_decision.reasoning,
            confidence=raw_decision.confidence,
        )
        await crud_ai_decision.create(db=db, obj_in=ai_decision_data)

        # 2. Sanitize and Validate
        safe_action = raw_decision.action.lower()
        if safe_action not in self.VALID_ACTIONS:
            logger.warning(f"Invalid AI action '{safe_action}'. Defaulting to 'hold'.")
            safe_action = "hold"
            
        if raw_decision.confidence < self.MIN_CONFIDENCE:
            logger.warning(f"AI confidence too low ({raw_decision.confidence}). Defaulting to 'hold'.")
            safe_action = "hold"
            
        safe_setpoint = raw_decision.setpoint
        if safe_setpoint < self.MIN_SETPOINT:
            logger.warning(f"AI setpoint too low ({safe_setpoint}). Clamping to {self.MIN_SETPOINT}.")
            safe_setpoint = self.MIN_SETPOINT
        elif safe_setpoint > self.MAX_SETPOINT:
            logger.warning(f"AI setpoint too high ({safe_setpoint}). Clamping to {self.MAX_SETPOINT}.")
            safe_setpoint = self.MAX_SETPOINT
            
        safe_fan_speed = raw_decision.fan_speed
        if safe_fan_speed < self.MIN_FAN_SPEED:
            logger.warning(f"AI fan speed too low ({safe_fan_speed}). Clamping to {self.MIN_FAN_SPEED}.")
            safe_fan_speed = self.MIN_FAN_SPEED
        elif safe_fan_speed > self.MAX_FAN_SPEED:
            logger.warning(f"AI fan speed too high ({safe_fan_speed}). Clamping to {self.MAX_FAN_SPEED}.")
            safe_fan_speed = self.MAX_FAN_SPEED

        # 3. Create the ControlAction
        control_action_data = ControlActionCreate(
            simulation_id=simulation_id,
            setpoint=safe_setpoint,
            fan_speed=safe_fan_speed,
            applied=False  # We'll set this to True if the physical layer accepts it
        )
        
        # 4. Apply to Physical Layer (Simulation)
        # Always apply the safe setpoint — even on 'hold' — so EnergyPlus
        # always has a valid in-range value injected each timestep.
        if eplus_service:
            success = eplus_service.apply_control_action(
                setpoint=safe_setpoint,
                fan_speed=safe_fan_speed
            )
            if success:
                control_action_data.applied = True
                
        # 5. Persist ControlAction
        db_control_action = await crud_control_action.create(db=db, obj_in=control_action_data)
        return db_control_action


# Singleton instance
decision_engine = DecisionEngineService()
