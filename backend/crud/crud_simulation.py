from crud.base import CRUDBase
from models.simulation import Simulation
from schemas.simulation import SimulationCreate, SimulationUpdate

class CRUDSimulation(CRUDBase[Simulation, SimulationCreate, SimulationUpdate]):
    pass

simulation = CRUDSimulation(Simulation)
