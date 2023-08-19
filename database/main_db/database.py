"""Модуль database.py осуществялет подключение
   к основной БД и создает все таблицы, хранящиеся в метаданных.
   По умолчанию не будет пересоздавать таблицы, если они уже присутсвуют в БД
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings


Base = declarative_base()
engine = create_engine(settings.MAIN_DB_URL)

Session = sessionmaker(bind=engine)


def create_db():
    """Создает все таблицы БД, хранящиеся в метаданных"""
    Base.metadata.create_all(bind=engine)