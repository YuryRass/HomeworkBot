"""
    Модуль homework_utils.py используется для создания
    pydantic моделей домашних заданий студентов.
    Преобразовает данные модели в JSON формат для их хранения
    в таблице 'assigned_discipline' в столбце 'home_work'
"""
import json
from pydantic.json import pydantic_encoder
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.home_work import DisciplineHomeWorks, HomeWork, HomeTask


def create_homeworks(discipline: DisciplineWorksConfig) -> DisciplineHomeWorks:
    """
        Создает и возвращает данные по лабораторным работам
    для учебной дисциплины.
        Параметры:
        discipline (DisciplineWorksConfig): учебная дисциплина.
    """
    # список лабораторных работ
    home_works_list: list[HomeWork] = []

    for it in discipline.works:
        # cписок домашних заданий
        home_tasks_list = [HomeTask(number=i)
                           for i in range(1, it.amount_tasks + 1)]
        home_work = HomeWork(
            number=it.number,
            deadline=it.deadline,
            tasks=home_tasks_list
        )
        home_works_list.append(home_work)
    return DisciplineHomeWorks(home_works=home_works_list)


def homeworks_from_json(json_data: str) -> DisciplineHomeWorks:
    """
        Конвертирует данные по лабораторным работам в pydantic модель
    'Лабораторные работы по учебной дисциплине' и возвращает их.
        Параметры:
        json_data (str): данные по лабораторным работам в JSON формате
    """
    data = json.loads(json_data)
    return DisciplineHomeWorks(**data)


def homeworks_to_json(data: DisciplineHomeWorks) -> str:
    """
        Преобразовывает данные pydantic модели
        'Лабораторные работы по учебной дисциплине' в JSON формат.
        Параметры:
        data (DisciplineHomeWorks): данные pydantic модели.
    """
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(',', ':'),
        default=pydantic_encoder
    )
