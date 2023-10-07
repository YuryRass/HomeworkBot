"""Модуль database.py осуществялет подключение
   к основной БД и создает все таблицы, хранящиеся в метаданных.
   По умолчанию не будет пересоздавать таблицы, если они уже присутсвуют в БД
"""
from typing_extensions import Annotated

from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import \
    AsyncSession, AsyncEngine, create_async_engine

from config import settings


# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     """Включение поддержки внешнего ключа"""
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

bigint = Annotated[int, "bigint"]


class Base(DeclarativeBase):
    type_annotation_map = {
        bigint: BigInteger()
    }


engine: AsyncEngine = create_async_engine(url=settings.MAIN_DB_URL)

Session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables() -> None:
    """Создает таблицы основной БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
