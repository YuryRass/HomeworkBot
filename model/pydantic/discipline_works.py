"""
    Создание pydantic модели DisciplinesConfig
"""
from datetime import date
from pydantic import BaseModel


class DisciplineWork(BaseModel):
    """
        Класс, описывающий pydantic модель 'Дисциплина'
        Атрибуты:
        number (int): номер дисциплины.
        amount_tasks (int): количество заданий.
        deadline (date): крайняя дата выполенения.
    """
    number: int
    amount_tasks: int
    deadline: date


class DisciplineWorksConfig(BaseModel):
    """
        Класс, описывающий pydantic модель 'Конфигурация работ дисциплины'
        Атрибуты:
        full_name (str): полное название дисциплины.
        short_name (str): сокращенное название дисциплины.
        path_to_test (str): путь до тестов для данной дисциплины.
        path_to_answer (str): путь до ответов, куда будут загружать студенты.
        language (str): язык программирования.
        works (list[DisciplineWork]): работы данной дисциплины.

    """
    full_name: str
    short_name: str
    path_to_test: str
    path_to_answer: str
    language: str
    works: list[DisciplineWork]


class DisciplinesConfig(BaseModel):
    """
        Класс, описывающий pydantic модель 'Конфигурация дисциплин'
        Атрибуты:
        disciplines (list[DisciplineWorksConfig]): список дисциплин.

    """
    disciplines: list[DisciplineWorksConfig]