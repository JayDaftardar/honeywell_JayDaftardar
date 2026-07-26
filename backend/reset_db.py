import asyncio
from sqlalchemy import text
from db.session import engine

async def reset_db():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE sensor_logs, ai_decisions, simulations CASCADE;"))
    print("Database reset successfully.")

if __name__ == "__main__":
    asyncio.run(reset_db())
