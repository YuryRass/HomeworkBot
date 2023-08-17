"""Модуль копируется в директорию из которой будет запускаться контейнер.
Содержит структуры данных для логирования результатов теста
и инициализации запускаемого теста
"""

from datetime import datetime

from pydantic import BaseModel


class TestLogInit(BaseModel):
    """Класс для именования файлов-логгеров"""
    student_id: int
    lab_id: int
    run_time: datetime


class TaskReport(BaseModel):
    """Отчет по учебному заданию"""
    task_id: int
    time: datetime
    status: bool
    description: set[str] = []


class LabReport(BaseModel):
    """Отчет по лаб. работе"""
    lab_id: int
    tasks: list[TaskReport] = []