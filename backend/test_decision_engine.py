import asyncio
from db.session import AsyncSessionLocal
from services.decision_engine import decision_engine
from services.llm_agent import AIDecision

from models.simulation import Simulation

async def test():
    # Construct a raw AI decision with slightly dangerous/out-of-bounds values
    # to ensure the Decision Engine clamps them correctly.
    raw_decision = AIDecision(
        action="reduce_setpoint",
        setpoint=15.0, # Too low! Should clamp to 18.0
        fan_speed=150.0, # Too high! Should clamp to 100.0
        reasoning="Testing decision engine bounds.",
        confidence=0.9
    )

    async with AsyncSessionLocal() as db:
        # Create mock simulation
        mock_sim = Simulation(status="running")
        db.add(mock_sim)
        await db.commit()
        await db.refresh(mock_sim)
        simulation_id = mock_sim.id
        
        print("Processing decision...")
        try:
            action = await decision_engine.process_decision(
                db=db,
                simulation_id=simulation_id,
                raw_decision=raw_decision,
                eplus_service=None
            )
            print("Successfully processed!")
            print(f"Applied action: {action.setpoint} setpoint, {action.fan_speed} fan speed")
            
            if action.setpoint == 18.0 and action.fan_speed == 100.0:
                print("Validation PASSED (Values were safely clamped)")
            else:
                print("Validation FAILED")
                
        except Exception as e:
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    asyncio.run(test())
