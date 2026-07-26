import asyncio
from sqlalchemy import text
from db.session import engine

async def main():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE simulations ADD COLUMN IF NOT EXISTS mode VARCHAR DEFAULT 'ai'"))
    print('Column added')

asyncio.run(main())
