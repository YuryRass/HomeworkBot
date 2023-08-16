"""Модуль, описывающий записи, которые хранятся во входной очереди"""
from pydantic import BaseModel


class QueueInRaw(BaseModel):
    """Записи во входной промежуточной очереди"""
    discipline_id: int
    lab_number: int
    files_path: list[str]