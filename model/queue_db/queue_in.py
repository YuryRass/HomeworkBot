"""Модуль реализуют таблицу с ответами студентов,
которые потом пойдут на проверку
"""

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database.queue_db import Base


class QueueIn(Base):
    __tablename__ = 'input'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f'Q(input) [tID: {self.telegram_id}, chatID:' + \
            f' {self.chat_id}, data: {self.data}'
