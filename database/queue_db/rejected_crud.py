"""Модуль реализует CRUD-операции с таблицей Rejected"""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.queue_db.database import Session
from model.pydantic.test_rejected_files import TestRejectedFiles
from model.queue_db.rejected import Rejected


async def add_record(
        user_tg_id: int,
        chat_id: int,
        rejected: TestRejectedFiles
) -> None:
    """Добавление записи в таблицу Rejected.

    Args:
        user_tg_id (int): ID телеграм пользователя.

        chat_id (int): ID телеграм чата.

        rejected (TestRejectedFiles): pydantic модель с файлами,
    которые не прошли тесты.
    """

    json_data = rejected.model_dump_json(indent=4, exclude_none=True)

    session: AsyncSession
    async with Session() as session:
        session.add(
            Rejected(
                telegram_id=user_tg_id,
                chat_id=chat_id,
                data=json_data
            )
        )
        await session.commit()
        await session.close()


async def is_empty() -> bool:
    """Пуста ли таблица Rejected.

    Returns:
        bool: True, если таблица пуста.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Rejected))
        data: list[Rejected] | [] = res.scalars().first()
        return not data


async def is_not_empty() -> bool:
    """Есть ли записи в таблице Rejected.

    Returns:
        bool: True, если записи есть в таблице.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Rejected))
        data: list[Rejected] | [] = res.scalars().first()
        return bool(data)


async def get_first_record() -> Rejected:
    """Получение первой записи из таблицы Rejected.
    После чего происходит удаление записи из таблицы.

    Returns:
        Rejected: запись из таблицы Rejected.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Rejected))
        record: Rejected = res.scalars().first()
        await session.execute(delete(Rejected).where(Rejected.id == record.id))
        await session.commit()
        return record
