from sqlalchemy import Column, Integer, JSON

from database.queue_db import Base


class QueueIn(Base):
    __tablename__ = 'input'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f'Q(input) [tID: {self.telegram_id}, chatID:' + \
            f' {self.chat_id}, data: {self.data}'
