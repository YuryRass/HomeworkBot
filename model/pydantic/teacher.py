"""
    Создание pydantic модели Teacher
"""
from pydantic import BaseModel


class Teacher(BaseModel):
    """
        Класс, описывающий pydantic модель 'Преподаватель'
        Атрибуты:
        full_name (str): ФИО препода.
        telegram_id (int): Telegram ID препода.
        is_admin (bool): флаг по проверке на админа.
        assign_disciplines (list[str]): дисциплины, назначенные преподу.
        assign_groups (list[str]): учебные группы, назначенные преподу.
    """
    full_name: str
    telegram_id: int
    is_admin: bool
    assign_disciplines: list[str]
    assign_groups: list[str]