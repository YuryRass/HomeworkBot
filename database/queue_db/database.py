"""Модуль для создания таблиц промежуточной БД"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings


class Base(DeclarativeBase):
    ...


engine = create_engine(url=settings.QUEUE_DB_URL)

Session = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)
