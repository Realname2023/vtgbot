import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from data_base.models import Base

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"

# engine = create_async_engine(DATABASE_URL, echo=True)

engine = create_async_engine(str(os.getenv('DB_URL')), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)



async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
