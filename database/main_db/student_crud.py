"""
    Модуль student_crud.py выполняет CRUD-операции с таблицей 'Student'
"""
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from database.main_db.database import Session

from model.main_db.student import Student
from model.main_db.discipline import Discipline


async def has_student(full_name: str) -> bool:
    """
        Возвращает True, если студент с именем
        full_name присутсвует в таблице 'Student'
        Параметры:
        full_name (str): полное имя студента.
    """
    session: AsyncSession
    async with Session() as session:
        smt = await session.execute(
            select(Student).
            where(Student.full_name.ilike(f'%{full_name}%'))
        )
        student: Student | None = smt.scalars().first()
        return student is not None


async def is_student(telegram_id: int) -> bool:
    """
        Возвращает True, если идентификатор студента
        telegram_id присутсвует в таблице 'Student'
        Параметры:
        telegram_id (int): идентификатор студента в Telegram.
    """
    session: AsyncSession
    async with Session() as session:
        smt = await session.execute(
            select(Student).
            where(Student.telegram_id == telegram_id)
        )
        student: Student | None = smt.scalars().first()
        return student is not None


async def set_telegram_id(full_name: str, telegram_id: int) -> None:
    """
        Обновляет атрибут telegram_id в таблице 'Student'
        для студента с ФИО = full_name.
        Параметры:
        full_name (str): полное имя студента (ФИО).
        telegram_id (int): новый идентификатор студента в Telegram.
    """
    session: AsyncSession
    async with Session() as session:
        smt = (
            update(Student).
            where(Student.full_name.ilike(f'%{full_name}%')).
            values(telegram_id=telegram_id)
        )
        await session.execute(smt)
        await session.commit()


async def get_student_by_tg_id(telegram_id: int) -> Student:
    """
    Функция запроса студента по идентификатору телеграмма

    :param telegram_id: телеграм id студента

    :return: Студент
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Student).
            where(Student.telegram_id == telegram_id)
        )
        student: Student = res.scalars().first()
        return student


async def get_assign_disciplines(student_tg_id: int) -> list[Discipline]:
    """Функция возвращает список дисциплин, назначенных студенту
    с Tg ID = student_tg_id

    Args:
        student_tg_id (int): ID студента в телеграмме.

    Returns:
        list[Discipline]: спсиок дисциплин.
    """
    session: AsyncSession
    async with Session() as session:
        smt = await session.execute(
            select(Student).
            options(joinedload(Student.group)).
            where(Student.telegram_id == student_tg_id)
        )
        student: Student = smt.scalars().first()

        return student.group.disciplines
