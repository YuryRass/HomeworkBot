"""Модуль для создания таблиц промежуточной БД"""

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import \
    AsyncEngine, create_async_engine, AsyncSession
from config import settings


class Base(DeclarativeBase):
    ...


engine: AsyncEngine = create_async_engine(url=settings.QUEUE_DB_URL)

Session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables() -> None:
    """Создает таблицы промежуточной БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
