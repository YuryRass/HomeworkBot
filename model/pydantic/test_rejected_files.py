"""Модуль описывает классы, хранящие информацию
   о проваленных заданиях (в результате вып-я тестов)
"""
from enum import IntEnum

from pydantic import BaseModel


class RejectedType(IntEnum):
    TemplateError = 0  # не вышел названием
    KeyWordsError = 1  # запрещенные или отсутствующие ключевые слова


class TestRejectedFiles(BaseModel):
    """Класс, описывающий файлы, которые не прошли тесты"""
    type: RejectedType
    description: str
    files: list[str]