from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.session import get_db
from crud.crud_sensor_log import sensor_log
from schemas.sensor_log import SensorLog
from core.websocket import manager

router = APIRouter()

@router.get("/history", response_model=List[SensorLog])
async def get_sensor_history(
    simulation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve historical sensor logs for a given simulation.
    """
    logs = await sensor_log.get_by_simulation(db, simulation_id=simulation_id, skip=skip, limit=limit)
    return logs

@router.websocket("/live")
async def websocket_sensor_live(websocket: WebSocket):
    """
    WebSocket endpoint for live sensor data broadcasting.
    """
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client in this one-way feed,
            # but we need to wait for receive to handle client disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
