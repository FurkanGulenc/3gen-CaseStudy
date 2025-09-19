import asyncio
from sqlalchemy import text
from app.db.base import AsyncSessionLocal

async def test_db_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print("DB Connection OK:", result.scalar_one())

from app.db.models import User
from sqlalchemy import select

async def test_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for u in users:
            print(f"User: {u.id} - {u.username} - {u.email}")

if __name__ == "__main__":
    asyncio.run(test_users())
