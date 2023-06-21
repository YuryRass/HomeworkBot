from sqlalchemy import Column, Integer
from database.main_db import Base


class StudentBan(Base):
    __tablename__ = 'banlist'

    telegram_id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f'StudentBan [ID: {self.telegram_id}]'
