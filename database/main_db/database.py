"""Модуль database.py осуществялет подключение
   к основной БД и создает все таблицы, хранящиеся в метаданных.
   По умолчанию не будет пересоздавать таблицы, если они уже присутсвуют в БД
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event

from config import settings


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Включение поддержки внешнего ключа"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    ...


engine = create_engine(url=settings.MAIN_DB_URL)

Session = sessionmaker(bind=engine)


def create_tables():
    """Создает таблицы основной БД"""
    Base.metadata.create_all(bind=engine)
