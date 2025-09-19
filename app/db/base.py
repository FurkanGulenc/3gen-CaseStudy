from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import DATABASE_URL  # config.py üzerinden oku

# Engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base
Base = declarative_base()

# ❌ BURADA MODELLERİ İMPORT ETME!
# from app.db.models import User, Project, OutputImage  (BUNU SİL)
# Çünkü circular import'a sebep oluyor.

# DB dependency
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
