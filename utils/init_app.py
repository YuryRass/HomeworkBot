"""
    Модуль init_app.py создает и инициализирует
    основную и промежуточную базы данных
"""

from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine

from database.main_db.database import engine as main_engine
from database.main_db.database_creator import create_main_tables
from database.queue_db.database import engine as queue_engine
from database.queue_db.database_creator import create_queue_tables
from model.pydantic.db_creator_settings import DbCreatorSettings

from config import settings


async def is_database_empty(engine: AsyncEngine) -> bool:
    """Проверка на наличие таблиц в БД

    Args:
        engine (AsyncEngine): асинхронный движок

    Returns:
        bool: True, если БД пуста, False - в противном случае
    """
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        return not tables


async def init_app() -> None:
    """Создание и инициализация баз данных"""

    # если основная база данных пуста, то добавляем туда
    # таблицы и инициализируем их
    if await is_database_empty(main_engine):
        db_settings = DbCreatorSettings(
            settings.REMOTE_CONFIGURATION,
            settings.DEFAULT_ADMIN,
            settings.PATH_TO_DISCIPLINES_DATA,
            settings.PATH_TO_INITIALIZATION_DATA
        )
        await create_main_tables(db_settings)

    # если промежуточная база данных пуста, то добавляем туда
    # таблицы и инициализируем их
    if await is_database_empty(queue_engine):
        await create_queue_tables()

    # создание директории для отчетов о студентах
    path = Path.cwd()
    Path(path.joinpath(settings.TEMP_REPORT_DIR)).mkdir(
        parents=True, exist_ok=True
    )
