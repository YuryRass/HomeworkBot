"""
Модуль копируется в директорию из которой будет запускаться контейнер
"""

import json
import os
from pathlib import Path
from threading import Lock
from .report_model import LabReport, TestLogInit, TaskReport



class _SingletonBaseClass(type):
    """Шаблон - одиночка."""
    _instances = {}  # словарь с экземплярами классов
    _lock: Lock = Lock()  # примитивный объект блокировки

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # в синхронном режиме
            # проверка на существование в словаре экземпляра класса
            if cls not in cls._instances:
                # добавляем экземпляр родит. класса в словарь
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        # если объект есть в словаре, то возвращаем его
        return cls._instances[cls]


class DockerLogger(metaclass=_SingletonBaseClass):
    """
    Класс для логирования результатов
    """
    def __init__(self):
        # заполнение pydantic-модель TestLogInit
        with open('log_init.json', encoding='utf-8') as fp:
            data = json.load(fp)
        self.test_settings = TestLogInit(**data)

        self.path_to_log = Path.cwd().joinpath('data').joinpath(
            f'{self.test_settings.student_id}' + \
            f'-{self.test_settings.lab_id}-' + \
            f'{self.test_settings.run_time:%Y-%m-%d_%H-%M-%S%z}.json'
        )

        # если файл-логгер существует, то считываем из него данные
        # о результатах проверки лаб. работы
        if os.path.isfile(self.path_to_log):
            with open(self.path_to_log, encoding='utf-8') as file:
                data = json.load(file)
                self.lab_report = LabReport(**data)
        # в противном случае - производим начальную инициализацию
        # переменной lab_report
        else:
            self.lab_report = LabReport(
                lab_id=self.test_settings.lab_id
            )

    def get_logfile_name(self) -> str:
        return self.path_to_log

    def add_successful_task(self, task_id: int) -> None:
        """
        Метод добавления задания, тест которого завершился успешно

        :param task_id: номер (идентификатор) задания

        :return: None
        """
        self.__add_task_report(task_id, True)

    def add_fail_task(self, task_id: int, description: str) -> None:
        """
        Метод добавления задания, тест которого провалился

        :param task_id: номер (идентификатор) задания
        :param description: описание причины провала

        :return: None
        """
        self.__add_task_report(task_id, False, description)

    def __add_task_report(
        self, task_id: int, status: bool, description: str | None = None
    ) -> None:
        """
        Метод добавления записи в лог файл результата тестирования

        :param task_id: номер (идентификатор) задания
        :param status: Если True - тест пройден, иначе - False
        :param description: описание причины провала или успеха

        :return: None
        """
        task = None  # будут содержать инфу о предыдущих тестах
        for it in self.lab_report.tasks:
            if task_id == it.task_id:
                task = it
                break

        # если информации о задаче task нет в lab_report,
        # то добавляем ее
        if task is None:
            self.lab_report.tasks.append(
                TaskReport(
                    task_id=task_id,
                    time=self.test_settings.run_time,
                    status=status,
                    description=[description] if description is not None
                    else []
                )
            )
        # task is not None
        else:  # обновляем данные в task
            if not (task.status and status):
                if task.status:  # task.status = True, status = False
                    task.status = False
                    task.description.add(description)
                else:
                    # task.status = False, status = False
                    if description is not None:
                        task.description.add(description)

    def save(self) -> None:
        """Сохранение результатов тестирования в JSON файл"""
        with open(self.path_to_log, 'w', encoding='utf-8') as fp:
            fp.write(
                self.lab_report.model_dump_json(
                    indent=4, exclude_none=True
                )
            )

