from pathlib import Path
import pytest

from database.main_db.database import engine as main_engine
from database.queue_db.database import engine as queue_engine

from utils.init_app import init_app


@pytest.fixture(scope='session', autouse=True)
def create_and_delete_all_tables():
    """
    Создает и заполняет базы данных
    и затем удаляет их, как пройдут все тесты
    """
    init_app()

    yield
    # закрываем все подключения
    main_engine.dispose()
    queue_engine.dispose()

    # удаляем все sql файлы
    for p in Path.cwd().glob("test_*.sqlite"):
        p.unlink()
