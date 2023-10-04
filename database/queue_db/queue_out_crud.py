"""Модуль реализует CRUD-операции с промежуточной таблицей QueueOut"""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.queue_db.database import Session
from model.pydantic.queue_out_raw import TestResult
from model.queue_db.queue_out import QueueOut


async def is_empty() -> bool:
    """Проверка на пустоту таблицы QueueOut.

    Returns:
        bool: True, если таблица пустая.
    """
    session: AsyncSession
    async with Session() as session:
        result = await session.execute(select(QueueOut))
        data: list[QueueOut] | [] = result.scalars().first()
        return not data


async def is_not_empty() -> bool:
    """Проверяет таблицу QueueOut на наличие в ней записей.

    Returns:
        bool: True, если таблица непустая.
    """
    session: AsyncSession
    async with Session() as session:
        result = await session.execute(select(QueueOut))
        data: list[QueueOut] | [] = result.scalars().first()
        return bool(data)


async def get_all_records() -> list[QueueOut]:
    """Возвращает список всех записей таблицы QueueOut.

    Returns:
        list[QueueOut]: список записей таблицы QueueOut.
    """
    # addresses = (await session.scalars(user.addresses.statement)).all()
    session: AsyncSession
    async with Session() as session:
        result = await session.execute(select(QueueOut))
        data: list[QueueOut] = result.scalars().all()
        return data


async def delete_record(record_id: int) -> None:
    """Удаление записи по ее ID в таблице QueueOut.

    Args:
        record_id (int): ID записи.
    """
    session: AsyncSession
    async with Session() as session:
        await session.execute(
            delete(QueueOut).where(QueueOut.id == record_id)
        )
        await session.commit()


async def add_record(user_tg_id: int, chat_id: int, data: TestResult) -> None:
    """Добавление записи в таблицу QueueOut.

    Args:
        user_tg_id (int): ID телеграм пользователя.
        chat_id (int): ID телеграм чата.
        data (TestResult): pydantic-данные о результататх тестирования.
    """

    # конвертируем pydantic данные в JSON формат
    json_data: str = data.model_dump_json(indent=4, exclude_none=True)

    session: AsyncSession
    async with Session() as session:
        session.add(
            QueueOut(
                telegram_id=user_tg_id,
                chat_id=chat_id,
                data=json_data
            )
        )
        await session.commit()
        await session.close()
