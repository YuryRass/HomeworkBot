"""
Модуль копируется в директорию из которой будет запускаться контейнер
"""

import pytest
from logger.docker_logger import DockerLogger


@pytest.fixture(scope="session")
def logger() -> DockerLogger:
    """Логгер для написания тестов."""
    return DockerLogger()


@pytest.fixture(scope='session', autouse=True)
def save_data():
    """
    Функция запускается после завершения всех тестов
    """
    yield
    logger = DockerLogger()
    logger.save()
