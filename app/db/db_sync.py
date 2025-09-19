from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Celery tarafı için senkron bağlantı
# URL'de asyncpg yerine psycopg2 kullanmalısın!
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

engine_sync = create_engine(SYNC_DATABASE_URL, echo=False, future=True)
SessionLocalSync = sessionmaker(bind=engine_sync, autoflush=False, autocommit=False)
