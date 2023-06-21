from sqlalchemy import Column, Integer
from database.main_db import Base


class Chat(Base):
    __tablename__ = 'chat'

    chat_id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f'Chat [ID: {self.chat_id}]'
