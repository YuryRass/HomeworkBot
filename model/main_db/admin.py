from sqlalchemy import Column, Integer, Boolean
from database.main_db import Base


class Admin(Base):
    __tablename__ = 'admin'

    telegram_id = Column(Integer, primary_key=True)
    teacher_mode = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f'Admin [ID: {self.telegram_id}, mode: {self.teacher_mode}]'
