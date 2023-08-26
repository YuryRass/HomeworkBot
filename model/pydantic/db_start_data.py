"""
    Создание pydantic модели, которая будет агрегировать другие модели
    и использоваться при первоначальной инициализации БД. Данная модель
    используется в случае, если параметр REMOTE_CONFIGURATION = True в '.env' файле
"""

from dataclasses import dataclass
from pydantic import BaseModel

from model.pydantic.students_group import StudentsGroup
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.teacher import Teacher


class DbStartData(BaseModel):
    """
        Класс, описывающий pydantic модель 'Первоначальные данные БД'
        Атрибуты:
        groups (list[StudentsGroup]): список студенческих групп.
        disciplines (list[DisciplineWorksConfig]): список учебных дисциплин.
        teachers (list[Teacher]): список преподавателей.
        chats (list[int]): список Tg-чатов.

    """
    groups: list[StudentsGroup]
    disciplines: list[DisciplineWorksConfig]
    teachers: list[Teacher]
    chats: list[int]


@dataclass
class StudentRaw:
    full_name: str


@dataclass
class TeacherRaw:
    full_name: str
    telegram_id: int
    is_admin: bool
