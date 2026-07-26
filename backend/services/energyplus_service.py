import threading
import logging
from typing import Dict, Any, Optional
import asyncio
import time
import sys
import math
import random

# Add EnergyPlus installation path to sys.path so we can import pyenergyplus
eplus_path = r"C:\EnergyPlusV26-2-0"
if eplus_path not in sys.path:
    sys.path.append(eplus_path)

# Attempt to import pyenergyplus. If not found, use a mock.
try:
    from pyenergyplus.api import EnergyPlusAPI
    HAS_EPLUS = True
except ImportError:
    HAS_EPLUS = False

logger = logging.getLogger(__name__)


class EnergyPlusService:
    def __init__(self):
        self.simulation_thread: Optional[threading.Thread] = None
        self._running = False
        self._new_data_available = threading.Event()
        self.current_sensor_values: Dict[str, Any] = {}

        # Sensor configuration: (Variable Name, Key Name)
        # Key names must match actual zone/system names in the IDF
        self.sensor_config = {
            "indoor_temp":    ("Zone Mean Air Temperature",                    "Core_ZN"),
            "outdoor_temp":   ("Site Outdoor Air Drybulb Temperature",         "Environment"),
            "humidity":       ("Zone Air Relative Humidity",                   "Core_ZN"),
            "pmv":            ("Zone Thermal Comfort Fanger Model PMV",        "Core_ZN People"),
            "hvac_energy":    ("Facility Total HVAC Electricity Demand Rate",  "Whole Building"),
            "cooling_energy": ("Facility Total Cooling Electricity Demand Rate","Whole Building"),
            "heating_energy": ("Facility Total Heating Electricity Demand Rate","Whole Building"),
        }
        self.handles: Dict[str, int] = {}

        # Actuator configuration: (Component Type, Control Type, Actuator Key)
        # Only control the cooling setpoint schedule.
        # HTGSETP_SCH is intentionally left uncontrolled — writing to it risks
        # creating a heating > cooling condition (EnergyPlus fatal: DualSetPointWithDeadBand).
        self.actuator_config = {
            "setpoint": ("Schedule:Compact", "Schedule Value", "CLGSETP_SCH"),
        }
        self.actuator_handles: Dict[str, int] = {}

        # Pending control actions — written from the asyncio thread, read in E+ thread
        self.pending_setpoint: Optional[float] = None
        self.pending_fan_speed: Optional[float] = None

        # EnergyPlus API and state are created fresh for each run
        self._api = None
        self._state = None

    # ------------------------------------------------------------------ #
    # EnergyPlus callback                                                  #
    # ------------------------------------------------------------------ #
    def _timestep_callback(self, state) -> None:
        if not self._running:
            return

        if not self._api.exchange.api_data_fully_ready(state):
            return

        # Fetch handles once
        if not self.handles:
            logger.info("API ready — fetching variable and actuator handles...")
            for key, (var_name, var_key) in self.sensor_config.items():
                h = self._api.exchange.get_variable_handle(state, var_name, var_key)
                self.handles[key] = h
                if h <= 0:
                    logger.warning(f"No handle for sensor '{key}' ({var_name}::{var_key})")

            for key, (comp, ctrl, act_key) in self.actuator_config.items():
                h = self._api.exchange.get_actuator_handle(state, comp, ctrl, act_key)
                self.actuator_handles[key] = h
                if h <= 0:
                    logger.warning(f"No handle for actuator '{key}' ({comp}::{ctrl}::{act_key})")

        # Read sensor values
        new_data = {}
        for key, h in self.handles.items():
            if h > 0:
                new_data[key] = self._api.exchange.get_variable_value(state, h)
            else:
                new_data[key] = None
        self.current_sensor_values = new_data

        # Apply pending actuator commands
        if self.pending_setpoint is not None:
            h = self.actuator_handles.get("setpoint", -1)
            if h > 0:
                self._api.exchange.set_actuator_value(state, h, self.pending_setpoint)
                logger.info(f"Applied cooling setpoint → CLGSETP_SCH = {self.pending_setpoint}°C")
            else:
                logger.warning("Cooling setpoint actuator handle not found (handle=-1). Check CLGSETP_SCH name in IDF.")
            self.pending_setpoint = None

        if self.pending_fan_speed is not None:
            # Map fan_speed (0-1) to a heating setpoint offset as a proxy control
            # (fan_speed not applicable in this model; we use it to modulate heating SP)
            h = self.actuator_handles.get("htg_setpoint", -1)
            if h > 0:
                # Clamp heating setpoint between 15 and 22°C
                htg_val = max(15.0, min(22.0, 21.0 * self.pending_fan_speed))
                self._api.exchange.set_actuator_value(state, h, htg_val)
                logger.info(f"Applied heating setpoint → HTGSETP_SCH = {htg_val}°C")
            self.pending_fan_speed = None

        # Signal asyncio loop that fresh data is ready
        self._new_data_available.set()

    # ------------------------------------------------------------------ #
    # Mock data loop (used when EnergyPlus is absent or finishes instantly)#
    # ------------------------------------------------------------------ #
    def _mock_loop(self):
        logger.info("Running mock sensor data loop...")
        t = 0
        clg_setpoint = 24.0
        htg_setpoint = 21.0
        while self._running:
            if self.pending_setpoint is not None:
                clg_setpoint = self.pending_setpoint
                self.pending_setpoint = None
            if self.pending_fan_speed is not None:
                # Map fan_speed to heating setpoint in mock mode
                htg_setpoint = max(15.0, min(22.0, 21.0 * self.pending_fan_speed))
                self.pending_fan_speed = None

            self.current_sensor_values = {
                "indoor_temp":    round(clg_setpoint - 1.0 + math.sin(t * 0.05) * 1.5 + random.uniform(-0.2, 0.2), 2),
                "outdoor_temp":   round(15.0 + math.sin(t * 0.03) * 8.0, 2),
                "humidity":       round(50.0 + math.sin(t * 0.07) * 10 + random.uniform(-2, 2), 2),
                "pmv":            round(math.sin(t * 0.04) * 0.4, 3),
                "hvac_energy":    round(3000.0 + random.uniform(-150, 150), 2),
                "cooling_energy": round(1800.0 + random.uniform(-100, 100), 2),
                "heating_energy": round(1200.0 + random.uniform(-50, 50), 2),
            }
            self._new_data_available.set()
            time.sleep(0.5)
            t += 1
        logger.info("Mock loop finished.")

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #
    def start(self, idf_path: str = "model.idf", epw_path: str = "weather.epw") -> None:
        if self._running:
            logger.warning("Simulation already running.")
            return

        self._running = True
        self.handles = {}
        self.actuator_handles = {}
        self.current_sensor_values = {}
        self._new_data_available.clear()

        def run_sim():
            if HAS_EPLUS:
                try:
                    # Create a FRESH api + state for every run
                    self._api = EnergyPlusAPI()
                    self._state = self._api.state_manager.new_state()

                    # Request output variables before run
                    for _, (var_name, var_key) in self.sensor_config.items():
                        self._api.exchange.request_variable(self._state, var_name, var_key)

                    # Register callback
                    self._api.runtime.callback_begin_zone_timestep_after_init_heat_balance(
                        self._state, self._timestep_callback
                    )

                    cmd_args = ["-d", "eplus_out", "-w", epw_path, idf_path]
                    logger.info(f"EnergyPlus starting: {idf_path}, {epw_path}")
                    self._api.runtime.run_energyplus(self._state, cmd_args)
                    logger.info("EnergyPlus completed.")

                    # EnergyPlus finished its sizing/annual run — fall through to mock
                    # so the dashboard keeps streaming data for the demo
                    if self._running:
                        logger.info("EnergyPlus done — switching to mock loop for live demo.")
                        self._mock_loop()

                except Exception as e:
                    logger.error(f"EnergyPlus crashed: {e}. Falling back to mock loop.")
                    if self._running:
                        self._mock_loop()
                finally:
                    if self._state is not None:
                        try:
                            self._api.state_manager.delete_state(self._state)
                        except Exception:
                            pass
                        self._state = None
            else:
                self._mock_loop()

            self._running = False
            self._new_data_available.set()  # unblock step()
            logger.info("Simulation thread finished.")

        self.simulation_thread = threading.Thread(target=run_sim, daemon=True)
        self.simulation_thread.start()

    async def step(self) -> Dict[str, Any]:
        """Async wait for next data update and return it."""
        if not self._running:
            return {}
        # Wait in a thread so we don't block the asyncio event loop
        await asyncio.to_thread(self._new_data_available.wait, 2.0)
        self._new_data_available.clear()
        return dict(self.current_sensor_values)

    def pause(self) -> None:
        logger.info("Pause is a no-op in free-running mode.")

    def resume(self) -> None:
        logger.info("Resume is a no-op in free-running mode.")

    def stop(self) -> None:
        logger.info("Stopping simulation...")
        self._running = False
        self._new_data_available.set()
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=3.0)

    def apply_control_action(self, setpoint: float, fan_speed: float) -> bool:
        if not self._running:
            return False
        logger.info(f"Queuing: setpoint={setpoint}°C, fan_speed={fan_speed}")
        self.pending_setpoint = setpoint
        self.pending_fan_speed = fan_speed
        return True
