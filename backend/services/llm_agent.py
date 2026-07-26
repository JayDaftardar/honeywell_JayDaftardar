import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from core.config import settings
from services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Output schema for the AI's response                                #
# ------------------------------------------------------------------ #
class AIDecision(BaseModel):
    action: str = Field(description="The HVAC action to take (e.g., 'reduce_setpoint', 'increase_fan_speed', 'hold')")
    setpoint: float = Field(description="Target temperature setpoint in degrees Celsius")
    fan_speed: float = Field(description="Fan speed as a percentage between 0 and 100")
    reasoning: str = Field(description="Plain-English explanation of why this decision was made")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")


# ------------------------------------------------------------------ #
# System prompt                                                        #
# ------------------------------------------------------------------ #
SYSTEM_PROMPT = """
You are an intelligent building energy manager controlling an HVAC system in a small office building.

Your objectives in order of priority:
1. Maintain occupant thermal comfort (PMV between -0.5 and +0.5 is ideal)
2. Minimise electricity consumption (HVAC energy and cooling energy)
3. Reduce carbon emissions

CRITICAL CONSTRAINTS — you MUST respect these at all times:
- Cooling setpoint MUST be between 23.0°C and 26.0°C (the building's heating setpoint is 21°C; EnergyPlus requires cooling > heating)
- Fan speed is a percentage between 0 and 100
- If the building is unoccupied or outdoor temperature is below 5°C, prefer a setpoint of 25–26°C to save energy

You will receive real-time sensor data. Analyse it and respond with a JSON object ONLY — no markdown, no explanation outside the JSON.

The JSON must have exactly these fields:
{
  "action": "<one of: reduce_setpoint | increase_setpoint | increase_fan_speed | reduce_fan_speed | hold>",
  "setpoint": <float, target temperature in °C, STRICTLY between 23.0 and 26.0>,
  "fan_speed": <float, percentage 0–100>,
  "reasoning": "<concise explanation>",
  "confidence": <float, 0.0–1.0>
}
""".strip()


class LLMAgentService:
    def __init__(self):
        # Initialize the abstracted LLM provider
        self.provider = get_llm_provider()

    async def initialize(self):
        """Optional async initialization to check health."""
        if not await self.provider.check_health():
            logger.warning("LLM Provider health check failed on initialization. The simulation loop may fail to get decisions.")

    def _build_user_prompt(self, sensor_data: Dict[str, Any]) -> str:
        """Format the sensor dict into a clear prompt for the LLM."""
        lines = ["Current building sensor readings:"]
        field_labels = {
            "indoor_temp":    "Indoor Temperature (°C)",
            "outdoor_temp":   "Outdoor Temperature (°C)",
            "humidity":       "Relative Humidity (%)",
            "pmv":            "PMV Comfort Index",
            "hvac_energy":    "HVAC Energy Demand (W)",
            "cooling_energy": "Cooling Energy Demand (W)",
            "heating_energy": "Heating Energy Demand (W)",
            "carbon":         "CO₂ Level (ppm)",
            "occupancy":      "Occupancy (persons)",
        }
        for key, label in field_labels.items():
            value = sensor_data.get(key)
            if value is not None:
                lines.append(f"  - {label}: {value}")
        lines.append("\nAnalyse these values and return your decision as JSON.")
        return "\n".join(lines)

    async def decide(self, sensor_data: Dict[str, Any]) -> Optional[AIDecision]:
        """
        Call the LLM provider with the current sensor data and parse the response
        into an AIDecision. Returns None on failure so the loop can continue.
        """
        user_prompt = self._build_user_prompt(sensor_data)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ]
        
        try:
            raw_text = await self.provider.chat_complete(
                messages=messages,
                temperature=0.2,  # Low temperature for consistent, reliable JSON
                max_tokens=512,
            )
            raw_text = raw_text.strip()
            logger.debug(f"LLM raw response: {raw_text}")

            # Parse JSON — strip any accidental markdown fences
            if raw_text.startswith("```"):
                # Handle cases where the model writes ```json or just ```
                parts = raw_text.split("```")
                if len(parts) >= 3:
                    raw_text = parts[1]
                else:
                    raw_text = parts[-1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            
            raw_text = raw_text.strip()

            parsed = json.loads(raw_text)
            decision = AIDecision(**parsed)
            logger.info(
                f"AI Decision: action={decision.action}, setpoint={decision.setpoint}, "
                f"fan_speed={decision.fan_speed}, confidence={decision.confidence}"
            )
            return decision

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}\nRaw: {raw_text}")
            return None
        except Exception as e:
            logger.error(f"LLM Provider call failed: {e}", exc_info=True)
            return None


# Module-level singleton
llm_agent = LLMAgentService()
