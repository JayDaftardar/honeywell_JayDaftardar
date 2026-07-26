import sys
import asyncio
sys.path.insert(0, '.')

from services.llm_agent import llm_agent

async def test():
    print("Initializing...")
    await llm_agent.initialize()
    print("Initialization done. Mocking data...")
    data = {
        'indoor_temp': 25.5,
        'pmv': 1.2,
        'hvac_energy': 500
    }
    print("Calling LLM...")
    res = await llm_agent.decide(data)
    print("Result:", res)

asyncio.run(test())
