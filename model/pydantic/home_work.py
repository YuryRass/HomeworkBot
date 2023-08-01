"""
    Создание pydantic модели DisciplineHomeWorks,
    данные которой будут храниться в таблице 'assigned_discipline'
    в столбце home_work в JSON формате
"""
from datetime import datetime, date
from pydantic import BaseModel


class HomeTask(BaseModel):
    """
        Класс, описывающий pydantic модель 'Домашнее задание'
        Атрибуты:
        number (int): номер задания.
        is_done (bool): флаг о выполнении задания.
        last_try_time (datetime): время последней попытки.
        amount_tries (int): количество попыток.
    """
    number: int
    is_done: bool = False
    last_try_time: datetime | None = None
    amount_tries: int = 0


class HomeWork(BaseModel):
    """
        Класс, описывающий pydantic модель 'Лабораторная работа'
        Атрибуты:
        number (int): номер лаб. работы.
        deadline (date): крайняя дата выполнения работы.
        tasks (list[HomeTask]): список заданий.
        is_done (bool): флаг о выполнении лаб. работы.
        end_time (datetime): время завершения.

    """
    number: int
    deadline: date
    tasks: list[HomeTask]
    is_done: bool = False
    end_time: datetime | None = None


class DisciplineHomeWorks(BaseModel):
    """
        Класс, описывающий pydantic модель
        'Лабораторные работы по учебной дисциплине'
        Атрибуты:
        home_works (list[HomeWork]): список лаб. работ.

    """
    home_works: list[HomeWork]