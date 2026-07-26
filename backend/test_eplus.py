import time
from services.energyplus_service import EnergyPlusService

def test_energyplus():
    print("Initializing EnergyPlusService...")
    service = EnergyPlusService()
    
    print("Starting simulation (Step mode)...")
    service.start(idf_path="dummy.idf", epw_path="dummy.epw")
    time.sleep(0.1) # Give thread time to start
    
    # Run a few steps
    for i in range(3):
        print(f"Executing step {i+1}...")
        data = service.step()
        print(f"Sensor Data: {data}")
        
        if i == 1:
            print("Applying a control action (setpoint=24.0, fan=75.0)...")
            service.apply_control_action(24.0, 75.0)
            
        time.sleep(0.5)
        
    print("Pausing simulation...")
    service.pause()
    time.sleep(1)
    
    print("Stopping simulation...")
    service.stop()
    print("Test completed.")

if __name__ == "__main__":
    test_energyplus()
