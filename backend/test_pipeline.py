import asyncio
from db.session import SessionLocal
from services.sensor_pipeline import SensorPipelineService

async def test_pipeline():
    # Provide a dummy simulation ID (assume 1 exists or mock it)
    simulation_id = 1
    
    # Mock data from EnergyPlusService._read_variables
    mock_data = {
        "indoor_temp": 24.5,
        "outdoor_temp": 30.1,
        "humidity": 45.0,
        "pmv": 0.3,
        "hvac_energy": 1200.0,
        "cooling_energy": 1000.0,
        "heating_energy": 0.0,
        "carbon": 300.0,
        "occupancy": 10.0
    }
    
    async with SessionLocal() as db:
        print("Saving mock data to DB and broadcasting...")
        # Need to handle foreign key constraint for simulation_id if simulation 1 doesn't exist.
        # But this is just a quick unit test structure.
        try:
            log = await SensorPipelineService.process_sensor_data(db, simulation_id, mock_data)
            print(f"Success! Created SensorLog ID: {log.id}")
        except Exception as e:
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
