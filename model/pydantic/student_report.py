"""
    Создание pydantic модели StudentReport
"""
from pydantic import BaseModel


class StudentReport(BaseModel):
    """
        Класс, описывающий pydantic модель 'Отчет об успеваемости студента'

        Атрибуты:

        full_name (str): ФИО студента.

        points (float): набранные баллы.

        lab_completed (int): количество завершенных лаб. работ.

        deadlines_fails (int): количество проваленных дедлайнов.

        task_completed (int): количесвто выполненных задач.

        task_ratio (int): соотношение выполненных задач. Если все задачи
    выполнены, то task_ratio = 1
    """
    full_name: str = ''
    points: float = 0
    lab_completed: int = 0
    deadlines_fails: int = 0
    task_completed: int = 0
    task_ratio: int = 0
