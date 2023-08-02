"""
    Модуль student_crud.py выполняет CRUD-операции с таблицей 'Student'
"""
from database.main_db.database import Session

from model.main_db.student import Student


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