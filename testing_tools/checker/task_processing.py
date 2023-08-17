"""Модуль реализует подистему тестирования"""

import asyncio
from pathlib import Path

from database.queue_db import queue_in_crud
from model.queue_db.queue_in import QueueIn


class TaskProcessing:
    """
    Главный класс подсистемы проверки
    """

    def __init__(
            self,
            temp_folder_path: Path,
            docker_amount_restriction: int = 1,
    ):
        """
        :param temp_folder_path: путь до временной директории, где будут формироваться
        каталоги для создания docker-контейнеров
        :param docker_amount_restriction: ограничение на количество одновременно работающих
        контейнеров
        """
        self.temp_folder_path = temp_folder_path
        self.docker_amount_restriction = docker_amount_restriction

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            for _ in range(self.docker_amount_restriction):
                tg.create_task(self.__task_processing())

    async def __task_processing(self):
        while True:
            await asyncio.sleep(2)
            if queue_in_crud.is_not_empty():
                record = queue_in_crud.get_first_record()
                await asyncio.gather(
                    asyncio.to_thread(
                        _run_prepare_docker,
                        record,
                        self.temp_folder_path,
                    )
                )


def _run_prepare_docker(record: QueueIn, temp_folder_path: Path) -> None:
    """
    Функция подготовки файлов для контейнера и его последующего запуска

    :param record: запись из промежуточной БД, с данными по загруженным ответам студента
    :param temp_folder_path: путь до временной директории, где будут формироваться
        каталоги для создания docker-контейнеров

    :return: None
    """
    ...