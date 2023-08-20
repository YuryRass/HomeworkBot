"""
    Модуль init_app.py создает и инициализирует
    основную и промежуточную базы данных
"""
import os
from pathlib import Path

from database.main_db.database_creator import create_main_db
from database.queue_db.database_creator import create_queue_db
from model.pydantic.db_creator_settings import DbCreatorSettings

from config import settings


def init_app() -> None:
    """Создание и инициализация баз данных"""

    # создание и инициализация основной БД
    db_is_created = os.path.exists(settings.DATABASE_NAME + '.sqlite')
    if not db_is_created:
        db_settings = DbCreatorSettings(
            settings.REMOTE_CONFIGURATION,
            settings.DEFAULT_ADMIN,
            settings.PATH_TO_DISCIPLINES_DATA,
            settings.PATH_TO_INITIALIZATION_DATA
        )
        create_main_db(db_settings)

    # создание и инициализация промежуточной БД
    db_is_created = os.path.exists(settings.QUEUE_DB_NAME + '.sqlite')
    if not db_is_created:
        create_queue_db()

    # создание директории для отчетов о студентах
    path = Path.cwd()
    Path(path.joinpath(settings.TEMP_REPORT_DIR)).mkdir(
        parents=True, exist_ok=True
    )
