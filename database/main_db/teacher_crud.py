"""
    Модуль teacher_crud.py выполняет CRUD-операции с таблицей 'Teacher'
"""
from database.main_db.database import Session

from model.main_db.teacher import Teacher


def is_teacher(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID
        принадлежит преподавателю.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    with Session() as session:
        teacher = session.query(Teacher).filter(
            Teacher.telegram_id == telegram_id
        ).first()
        return teacher is not None