"""
    Модуль teacher_crud.py выполняет CRUD-операции,
    необхимые преподаваетлю, с БД
"""
from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.main_db.database import Session

from model.main_db.admin import Admin
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.discipline import Discipline
from model.main_db.student import Student


async def is_teacher(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID
        принадлежит преподавателю.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).where(Teacher.telegram_id == telegram_id)
        )
        teacher: Teacher | None = res.scalars().first()
        return teacher is not None


async def get_assign_group_discipline(
    teacher_tg_id: int, group_id: int
) -> list[Discipline]:
    """
    Функция запроса списка дисциплин, которые числятся
    за преподавателем у конкретной группы

    :param teacher_tg_id: телеграм идентификатор преподавателя
    :param group_id: идентификатор группы

    :return: список дисциплин
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).options(selectinload(Teacher.disciplines)).
            where(Teacher.telegram_id == teacher_tg_id)
        )
        teacher: Teacher = res.scalars().first()

        teacher_set = {it.short_name for it in teacher.disciplines}

        group: Group = await session.get(Group, group_id)

        group_set = {it.short_name for it in group.disciplines}

        return [it for it in teacher.disciplines
                if it.short_name in teacher_set.intersection(group_set)]


async def switch_teacher_mode_to_admin(teacher_tg_id: int) -> None:
    session: AsyncSession
    async with Session() as session:
        smt = (
            update(Admin).
            where(Admin.telegram_id == teacher_tg_id).
            values(teacher_mode=False)
        )
        await session.execute(smt)
        await session.commit()


async def get_assign_groups(teacher_tg_id: int) -> list[Group]:
    """
    Функция запроса списка групп, у которых ведет предметы преподаватель

    :param teacher_tg_id: телеграм идентификатор преподавателя

    :return: список групп
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).
            options(selectinload(Teacher.groups)).
            where(Teacher.telegram_id == teacher_tg_id)
        )
        teacher: Teacher = res.scalars().first()
        return teacher.groups


async def get_teacher_disciplines(teacher_tg_id: int) -> list[Discipline]:
    """
    Функция запроса списка дисциплин, которые числятся за преподавателем

    :param teacher_tg_id: телеграм идентификатор преподавателя

    :return: список дисциплин
    """
    session: AsyncSession
    async with Session() as session:
        smt = await session.execute(
            select(Teacher).
            options(selectinload(Teacher.disciplines)).
            where(Teacher.telegram_id == teacher_tg_id)
        )
        teacher: Teacher = smt.scalars().first()
        return teacher.disciplines


async def get_auth_students(group_id: int) -> list[Student]:
    """Функция возвращает список авторизованных студентов.

    Args:
        group_id (int): ID учебной группы.

    Returns:
        list[Student]: список авторизованных студентов.
    """
    session: AsyncSession
    async with Session() as session:
        smt = await session.execute(
            select(Student).
            where(
                and_(
                    Student.group_id == group_id,
                    Student.telegram_id.is_not(None),
                )
            )
        )
        students: list[Student] = smt.scalars().all()
        return students
