from enum import Enum

from database.main_db.database import Session

from model.main_db.admin import Admin
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.chat import Chat
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student


class UserEnum(Enum):
    """
        Класс, описывающий всевозможные типы Telegram пользователей
    """
    Admin = 0
    Teacher = 1
    Student = 2
    Unknown = 3


def user_verification(telegram_id: int) -> UserEnum:
    """
        Аутентификация Telegram пользователя
        Параметры:
        telegram_id (int): Telegram ID пользователя.
    """
    with Session() as session:
        # проверка на админа
        user = session.query(Admin).get(telegram_id)
        if user is not None:
            return UserEnum.Admin

        # проверка на препода
        user = session.query(Teacher).filter(
            Teacher.telegram_id == telegram_id
        ).first()
        if user is not None:
            return UserEnum.Teacher

        # проверка на студента
        user = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        if user is not None:
            return UserEnum.Student

    # неизвестный пользователь
    return UserEnum.Unknown


def get_chats() -> list[int]:
    """
        Получение списка с идентифкаторами Tg-чатов.
    """
    with Session() as session:
        chats = session.query(Chat).all()
        return [it.chat_id for it in chats]

def get_group_disciplines(group_id: int) -> list[Discipline]:
    """
        Возвращает список дисциплин для учебной группы.
        Параметры:
        group_id (int): ID учебной группы
    """
    with Session() as session:
        disciplines = session.query(Discipline).join(
            AssignedDiscipline,
            AssignedDiscipline.discipline_id == Discipline.id
        ).join(
            Student,
            Student.id == AssignedDiscipline.student_id
        ).filter(Student.group == group_id).all()
        return disciplines
    # with Session() as session:
    #     student = session.query(Student).filter(
    #         Student.group == group_id
    #     ).first()
    #     assigned_disciplines = session.query(AssignedDiscipline).filter(
    #         AssignedDiscipline.student_id == student.id
    #     ).all()
    #     assigned_disciplines = [it.discipline_id for it in assigned_disciplines]
    #     disciplines = session.query(Discipline).filter(
    #         Discipline.id.in_(assigned_disciplines)
    #     ).all()
    #     return disciplines