"""
    Создание pydantic модели StudentsGroup
"""
from pydantic import BaseModel


class StudentsGroup(BaseModel):
    """
        Класс, описывающий pydantic модель 'Группа студентов'
        Атрибуты:
        group_name (str): название учебной группы.
        disciplines_short_name (list[str]): сокращенные названия
    дисциплин данной учебной группы.
        students (list[str]): список студентов данной учебной группы.
    """
    group_name: str
    disciplines_short_name: list[str]
    students: list[str]
