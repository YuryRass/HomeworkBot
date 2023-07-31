"""Модуль database.py осуществялет подключение
   к основной БД и создает все таблицы, хранящиеся в метаданных.
   По умолчанию не будет пересоздавать таблицы, если они уже присутсвуют в БД
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import load_config, Config


# Загрузка данных из файла .env
config: Config = load_config()
Base = declarative_base()
engine = create_engine(f'sqlite:///{config.db.database_name}.sqlite')

Session = sessionmaker(bind=engine)


def create_db():
    """Создает все таблицы БД, хранящиеся в метаданных"""
    Base.metadata.create_all(bind=engine)