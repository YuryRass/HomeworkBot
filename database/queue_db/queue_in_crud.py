"""Модуль, реализующий CRUD-операции с промежуточн. таблицей QueueIn"""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.pydantic.queue_in_raw import QueueInRaw

from database.queue_db.database import Session
from model.queue_db.queue_in import QueueIn


async def add_record(user_tg_id: int, chat_id: int, data: QueueInRaw) -> None:
    """Добавление записи в промеж. таблицу QueueIn

    Args:
        user_tg_id (int): Tg ID пользователя.
        chat_id (int): ID Tg чата.
        data (QueueInRaw): данные для добавления в таблицу.
    """
    json_data: str = data.model_dump_json(indent=4, exclude_none=True)

    session: AsyncSession
    async with Session() as session:
        session.add(
            QueueIn(
                telegram_id=user_tg_id,
                chat_id=chat_id,
                data=json_data
            )
        )
        await session.commit()
        await session.close()


async def is_empty() -> bool:
    """Проверяет пуста ли таблица QueuIn"""
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(QueueIn))
        data: list[QueueIn] | [] = res.scalars().first()
        return not data


async def is_not_empty() -> bool:
    """Проверяет не пуста ли таблица QueuIn"""
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(QueueIn))
        data: list[QueueIn] | [] = res.scalars().first()
        return bool(data)


async def get_first_record() -> QueueIn:
    """Возвращает первую запись из таблицы QueueIn"""
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(QueueIn))
        record: QueueIn = res.scalars().first()
        await session.execute(delete(QueueIn).where(QueueIn.id == record.id))
        await session.commit()
        return record
