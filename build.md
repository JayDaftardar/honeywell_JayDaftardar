\# Smart Building AI

\## Autonomous Closed-Loop Energy Optimization using EnergyPlus + Mistral + MCP



\---



\# Overview



This project is being built for a hackathon.



The objective is to create an autonomous AI-powered Building Management System (BMS) that continuously optimizes energy usage inside a building.



Instead of using traditional rule-based schedules, an LLM observes the building state, reasons over live sensor values, decides optimal Energy Conservation Measures (ECMs), and automatically applies those changes back into the EnergyPlus simulation.



The complete pipeline is:



EnergyPlus

→ Sensor Data

→ FastAPI

→ Mistral LLM

→ Decision Engine

→ Validation

→ EnergyPlus

→ Repeat



This forms a fully autonomous closed-loop control system.



\---



\# Primary Goal



The project must demonstrate:



\- autonomous decision making

\- closed-loop control

\- measurable energy savings

\- thermal comfort preservation

\- explainable AI reasoning

\- modern software architecture



The project is NOT just a chatbot.



The AI must actually control the simulation.



\---



\# Technology Stack



Frontend



\- React

\- Vite

\- TailwindCSS

\- Recharts

\- React Query



Backend



\- FastAPI

\- SQLAlchemy

\- Alembic

\- PostgreSQL

\- NeonDB



AI



\- Mistral API

\- MCP Server

\- Tool Calling



Simulation



\- EnergyPlus

\- PyEnergyPlus API



Realtime



\- WebSockets



Charts



\- Recharts



Deployment



Frontend

Vercel



Backend

Render/Railway



Database

Neon PostgreSQL



\---



\# High Level Architecture



&#x20;                   React Dashboard

&#x20;                          |

&#x20;                   REST + WebSocket

&#x20;                          |

&#x20;                   FastAPI Backend

&#x20;                          |

&#x20;    ------------------------------------------

&#x20;    |          |          |         |         |

&#x20;EnergyPlus   MCP      Mistral   Database   Scheduler

&#x20;    |          |          |

&#x20;     ----------|----------

&#x20;               |

&#x20;       Decision Engine

&#x20;               |

&#x20;       Safety Validation

&#x20;               |

&#x20;       Update Setpoints

&#x20;               |

&#x20;         EnergyPlus



\---



\# Folder Structure



smart-building-ai/



frontend/



backend/



energyplus/



agent/



mcp/



database/



docs/



videos/



README.md



\---



\# Coding Standards



Always use



\- Python typing

\- Pydantic models

\- SQLAlchemy ORM

\- Async FastAPI

\- Service Layer pattern

\- Repository pattern where appropriate

\- Environment variables

\- Clean architecture



Never put business logic inside API routes.



Routes should only call services.



\---



\# Communication Flow



EnergyPlus



↓



Sensor Collector



↓



FastAPI



↓



Database



↓



Mistral Agent



↓



Decision



↓



Validator



↓



EnergyPlus



↓



Next timestep



\---



\# Database Design



Tables



simulations



sensor\_logs



control\_actions



ai\_decisions



users (optional)



\---



\# APIs



Simulation



POST /simulation/start



POST /simulation/pause



POST /simulation/stop



GET /simulation/status



GET /simulation/history



Sensors



GET /sensor/live



GET /sensor/history



AI



POST /agent/decide



GET /agent/history



Dashboard



GET /dashboard/summary



GET /dashboard/charts



\---



\# Dashboard Pages



Home



Simulation



Dashboard



Analytics



AI Decisions



Reports



Settings



\---



\# Important Rule



DO NOT implement everything at once.



Implement one module completely before moving to the next.



Every module must be independently testable.



Every module must compile before continuing.



\---



\# IMPLEMENTATION ROADMAP



\---



\# MODULE 1



Project Setup



Goal



Create the complete project structure.



Tasks



\- Initialize React

\- Initialize FastAPI

\- Configure Tailwind

\- Configure PostgreSQL

\- Configure Alembic

\- Configure environment variables



Deliverable



Working frontend and backend.



Stop after completing this module.



\---



\# MODULE 2



Database



Goal



Create all database models.



Tables



simulations



sensor\_logs



control\_actions



ai\_decisions



Tasks



Create



\- SQLAlchemy models

\- Pydantic schemas

\- CRUD layer

\- Alembic migrations



Deliverable



Database working.



Stop after completion.



\---



\# MODULE 3



EnergyPlus Integration



Goal



Integrate EnergyPlus.



Tasks



Load IDF



Run simulation



Read variables



Read timestep values



Return sensor values



Create



EnergyPlusService



Methods



start()



stop()



pause()



resume()



step()



Deliverable



EnergyPlus can run from Python.



Stop.



\---



\# MODULE 4



Sensor Pipeline



Goal



Collect simulation data.



Collect



Indoor temperature



Outdoor temperature



Humidity



PMV



HVAC Energy



Cooling



Heating



Carbon



Occupancy



Convert to JSON



Store in database



Broadcast using WebSocket



Deliverable



Live sensor pipeline.



Stop.



\---



\# MODULE 5



Simulation Controller



Goal



Control the simulation.



Create



SimulationRunner



Responsibilities



Run timestep



Collect data



Store database



Broadcast websocket



Wait for AI



Continue simulation



Deliverable



Simulation controller complete.



Stop.



\---



\# MODULE 6



Mistral Integration



Goal



Integrate Mistral API.



Prompt



You are an intelligent building energy manager.



Objectives



Reduce electricity.



Maintain comfort.



Reduce carbon.



Return JSON only.



Expected Output



{

&#x20;   action,

&#x20;   setpoint,

&#x20;   fan\_speed,

&#x20;   reasoning,

&#x20;   confidence

}



Deliverable



LLM responding correctly.



Stop.



\---



\# MODULE 7



Decision Engine



Goal



Interpret AI output.



Responsibilities



Parse JSON



Validate output



Reject dangerous values



Accept valid values



Deliverable



Safe decisions.



Stop.



\---



\# MODULE 8



MCP Server



Goal



Create MCP tools.



Tools



read\_sensor\_data



read\_weather



update\_setpoint



simulation\_status



energy\_history



comfort\_history



run\_next\_step



save\_report



Deliverable



Working MCP server.



Stop.



\---



\# MODULE 9



Closed Loop



Goal



Create autonomous loop.



Flow



EnergyPlus



↓



Sensor



↓



Mistral



↓



Decision



↓



Validation



↓



EnergyPlus



↓



Repeat



Deliverable



Autonomous optimization.



Stop.



\---



\# MODULE 10



Dashboard



Goal



Build frontend.



Cards



Energy



Temperature



Humidity



Carbon



PMV



Occupancy



Charts



Energy



Temperature



Carbon



Cooling



Heating



Controls



Start



Pause



Resume



Stop



Deliverable



Complete dashboard.



Stop.



\---



\# MODULE 11



Analytics



Goal



Compare baseline with AI.



Metrics



Energy



Cost



Carbon



Comfort



Savings %



Charts



Before



After



Deliverable



Comparison dashboard.



Stop.



\---



\# MODULE 12



Reports



Goal



Generate reports.



Include



Graphs



Energy savings



Carbon savings



AI decisions



Comfort metrics



Deliverable



PDF report.



Stop.



\---



\# MODULE 13



Testing



Goal



Test everything.



Verify



Simulation



AI



Database



Dashboard



WebSockets



EnergyPlus



Deliverable



Stable application.



Stop.



\---



\# Definition of Done



The project is complete only if



✓ EnergyPlus runs



✓ Live data is streamed



✓ AI receives live data



✓ AI makes decisions



✓ Decisions are validated



✓ EnergyPlus receives updated setpoints



✓ Dashboard updates live



✓ Baseline comparison works



✓ Reports generated



✓ Energy savings demonstrated



✓ Thermal comfort maintained



✓ AI reasoning visible



\---



\# Instructions for Antigravity



For every module:



1\. Explain the implementation approach.

2\. Generate production-quality code.

3\. Explain folder/file changes.

4\. Explain APIs created.

5\. Explain database changes.

6\. Explain how to test the module.

7\. Do NOT proceed to the next module until this module is complete.

8\. Keep code modular and reusable.

9\. Use best engineering practices.

10\. Do not use placeholder implementations unless explicitly requested.



The objective is to build a production-quality Proof of Concept suitable for a hackathon demonstration while keeping the architecture clean, modular, and extensible.

