"""
    Модуль init_app.py создает и инициализирует
    основную и промежуточную базы данных
"""

from pathlib import Path

from sqlalchemy_utils import database_exists, create_database

from database.main_db.database import engine as main_engine
from database.main_db.database_creator import create_main_tables
from database.queue_db.database import engine as queue_engine
from database.queue_db.database_creator import create_queue_tables
from model.pydantic.db_creator_settings import DbCreatorSettings

from config import settings


def init_app() -> None:
    """Создание и инициализация баз данных"""

    # создание основной БД и добавление туда таблиц
    if not database_exists(main_engine.url):
        create_database(main_engine.url)
        db_settings = DbCreatorSettings(
            settings.REMOTE_CONFIGURATION,
            settings.DEFAULT_ADMIN,
            settings.PATH_TO_DISCIPLINES_DATA,
            settings.PATH_TO_INITIALIZATION_DATA
        )
        create_main_tables(db_settings)

    # создание промежуточной БД и добавление туда таблиц
    if not database_exists(queue_engine.url):
        create_database(queue_engine.url)
        create_queue_tables()

    # создание директории для отчетов о студентах
    path = Path.cwd()
    Path(path.joinpath(settings.TEMP_REPORT_DIR)).mkdir(
        parents=True, exist_ok=True
    )
