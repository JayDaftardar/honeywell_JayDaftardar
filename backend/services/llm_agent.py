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
You are an intelligent HVAC energy optimization AI for a commercial office building.

CONTEXT:
- The standard/baseline thermostat schedule is fixed at 24°C cooling setpoint.
- Your job is to REDUCE energy consumption by raising the setpoint when safe to do so.
- Higher cooling setpoint = less cooling energy used = better efficiency.

OBJECTIVES (in order of priority):
1. MINIMIZE ENERGY: Reduce HVAC electricity consumption vs the 24°C baseline.
2. MAINTAIN COMFORT: Keep PMV between -0.5 and +0.5 (occupant comfort).
3. When outdoor temperature is high (>30°C), a setpoint of 25–26°C is IDEAL.

MANDATORY CONSTRAINTS — you MUST respect these:
- Cooling setpoint MUST be between 23.0°C and 26.0°C (hard limits, never exceed).
- The DEFAULT should be 25.0°C or 26.0°C — only go to 23–24°C if PMV > +0.4 (too warm).
- Fan speed between 0 and 100.
- If PMV is already comfortable (-0.3 to +0.3), ALWAYS choose setpoint >= 25.0°C.

Respond with a JSON object ONLY — no markdown, no text outside the JSON.

The JSON must have exactly these fields:
{
  "action": "<one of: reduce_setpoint | increase_setpoint | hold>",
  "setpoint": <float between 23.0 and 26.0, DEFAULT to 25.0 or 26.0>,
  "fan_speed": <float, percentage 0–100>,
  "reasoning": "<concise explanation referencing the sensor values>",
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
