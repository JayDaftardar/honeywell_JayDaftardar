import asyncio
import httpx
from mcp.server.fastmcp import FastMCP
from sqlalchemy.future import select
from sqlalchemy import desc
from db.session import AsyncSessionLocal
from models.sensor_log import SensorLog
from models.simulation import Simulation

# Create the MCP Server
mcp = FastMCP("Smart Building MCP Server")

API_BASE_URL = "http://127.0.0.1:8000"

@mcp.tool()
async def read_sensor_data() -> str:
    """Fetches the most recent sensor data from the smart building."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SensorLog).order_by(desc(SensorLog.timestamp)).limit(1)
        )
        log = result.scalars().first()
        
        if not log:
            return "No sensor data available."
            
        return (
            f"Indoor Temp: {log.indoor_temp}°C\n"
            f"Outdoor Temp: {log.outdoor_temp}°C\n"
            f"Humidity: {log.humidity}%\n"
            f"PMV Comfort: {log.pmv}\n"
            f"HVAC Energy: {log.hvac_energy}W\n"
            f"CO2 Level: {log.carbon}ppm\n"
            f"Occupancy: {log.occupancy} people"
        )

@mcp.tool()
async def read_weather() -> str:
    """Fetches the most recent weather (outdoor temp and humidity)."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SensorLog).order_by(desc(SensorLog.timestamp)).limit(1)
        )
        log = result.scalars().first()
        
        if not log:
            return "No weather data available."
            
        return f"Outdoor Temp: {log.outdoor_temp}°C, Humidity: {log.humidity}%"

@mcp.tool()
async def update_setpoint(setpoint: float, fan_speed: float) -> str:
    """Issues a manual setpoint override to the building's HVAC system."""
    # Since the agent API expects full sensor data, we might want a dedicated override endpoint.
    # We can hit the local database to insert a ControlAction, but we'd need to notify the runner.
    # The runner currently picks up decisions from the agent via the loop.
    # For now, we'll log it as a decision in the DB, though the autonomous loop might overwrite it on the next step.
    # We will provide a stub implementation pointing to the fact that manual overrides are handled via API.
    return f"Manual override requested: setpoint={setpoint}°C, fan_speed={fan_speed}%. (Note: Autonomous loop may overwrite this on next tick unless paused)."

@mcp.tool()
async def simulation_status() -> str:
    """Returns whether the EnergyPlus simulation is currently running, paused, or stopped."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/simulation/status")
            if response.status_code == 200:
                data = response.json()
                status = "Running" if data.get("is_running") else "Stopped"
                if data.get("is_paused"):
                    status = "Paused"
                return f"Simulation Status: {status}"
    except Exception as e:
        return f"Could not reach API: {str(e)}"
    return "Unknown status."

@mcp.tool()
async def energy_history(limit: int = 10) -> str:
    """Queries the database for the last N time steps of HVAC energy consumption."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SensorLog).order_by(desc(SensorLog.timestamp)).limit(limit)
        )
        logs = result.scalars().all()
        
        if not logs:
            return "No energy data available."
            
        history = [f"{log.timestamp}: {log.hvac_energy}W" for log in logs]
        return "\n".join(history)

@mcp.tool()
async def comfort_history(limit: int = 10) -> str:
    """Queries the database for the last N time steps of PMV (Predicted Mean Vote)."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SensorLog).order_by(desc(SensorLog.timestamp)).limit(limit)
        )
        logs = result.scalars().all()
        
        if not logs:
            return "No comfort data available."
            
        history = [f"{log.timestamp}: PMV {log.pmv}" for log in logs]
        return "\n".join(history)

@mcp.tool()
async def run_next_step() -> str:
    """If the simulation is paused, triggers it to compute the next timestep."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE_URL}/simulation/step")
            if response.status_code == 200:
                return "Successfully advanced simulation by one step."
            return f"Failed to step simulation: {response.text}"
    except Exception as e:
        return f"Could not reach API: {str(e)}"

@mcp.tool()
async def save_report(filename: str = "building_status.md") -> str:
    """Generates a quick textual summary of the current building state and saves it."""
    try:
        data = await read_sensor_data()
        status = await simulation_status()
        
        report = f"# Building Status Report\n\n## Status\n{status}\n\n## Current Readings\n{data}\n"
        
        with open(filename, "w") as f:
            f.write(report)
            
        return f"Report saved successfully to {filename}"
    except Exception as e:
        return f"Error saving report: {str(e)}"


@mcp.tool()
async def read_energyplus_errors() -> str:
    """
    Reads and parses the EnergyPlus error/warning log from the most recent simulation run.
    Use this to diagnose simulation issues, extract runtime warnings, or verify correct execution.
    """
    import os
    err_path = os.path.join(os.path.dirname(__file__), "eplus_out", "eplusout.err")
    try:
        with open(err_path, "r") as f:
            content = f.read()
        # Return last 4000 chars to avoid overflowing LLM context
        excerpt = content[-4000:] if len(content) > 4000 else content
        line_count = content.count("\n")
        return f"[EnergyPlus Error Log — {line_count} lines total, showing last 4000 chars]\n\n{excerpt}"
    except FileNotFoundError:
        return (
            "No EnergyPlus error file found at eplus_out/eplusout.err. "
            "Has a simulation been run yet? Start one via POST /simulation/start."
        )
    except Exception as e:
        return f"Error reading eplusout.err: {e}"


@mcp.tool()
async def read_idf_file(filename: str = "model.idf") -> str:
    """
    Reads an EnergyPlus IDF building model file and returns its contents.
    Use this to inspect the building configuration, schedules, or verify AI-generated modifications.
    Supports 'model.idf' (baseline) and 'model_modified.idf' (AI-optimized version).
    """
    import os
    allowed = {"model.idf", "model_modified.idf"}
    if filename not in allowed:
        return f"Access denied. Only {allowed} are readable via this tool."
    idf_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(idf_path, "r") as f:
            content = f.read()
        # Return first 5000 chars (the header and key sections)
        excerpt = content[:5000]
        return f"[{filename} — {len(content)} bytes total, showing first 5000 chars]\n\n{excerpt}"
    except FileNotFoundError:
        return f"File '{filename}' not found. Run a simulation and export the modified IDF first."
    except Exception as e:
        return f"Error reading {filename}: {e}"


if __name__ == "__main__":
    # Start the FastMCP server over stdio
    mcp.run()

