"""
    Модуль student_crud.py выполняет CRUD-операции с таблицей 'Student'
"""
from database.main_db.database import Session

from model.main_db.student import Student
from model.main_db.discipline import Discipline


def has_student(full_name: str) -> bool:
    """
        Возвращает True, если студент с именем
        full_name присутсвует в таблице 'Student'
        Параметры:
        full_name (str): полное имя студента.
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.full_name.ilike(f'%{full_name}%')
        ).first()
        return student is not None


def is_student(telegram_id: int) -> bool:
    """
        Возвращает True, если идентификатор студента
        telegram_id присутсвует в таблице 'Student'
        Параметры:
        telegram_id (int): идентификатор студента в Telegram.
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        return student is not None


def set_telegram_id(full_name: str, telegram_id: int) -> None:
    """
        Обновляет атрибут telegram_id в таблице 'Student'
        для студента с ФИО = full_name.
        Параметры:
        full_name (str): полное имя студента (ФИО).
        telegram_id (int): новый идентификатор студента в Telegram.
    """
    with Session() as session:
        session.query(Student).filter(
            Student.full_name.ilike(f'%{full_name}%')
        ).update(
            {Student.telegram_id: telegram_id}, synchronize_session='fetch'
        )
        session.commit()


def get_student_by_tg_id(telegram_id: int):
    """
    Функция запроса студента по идентификатору телеграмма

    :param telegram_id: телеграм id студента

    :return: Студент
    """
    with Session() as session:
        student = (
            session.query(Student).filter(
                Student.telegram_id == telegram_id
            ).first()
        )
        return student


def get_assign_disciplines(student_tg_id: int) -> list[Discipline]:
    """Функция возвращает список дисциплин, назначенных студенту
    с Tg ID = student_tg_id

    Args:
        student_tg_id (int): ID студента в телеграмме.

    Returns:
        list[Discipline]: спсиок дисциплин.
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == student_tg_id
        ).first()

        return student.group.disciplines
