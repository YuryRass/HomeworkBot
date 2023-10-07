import json
from datetime import datetime
from enum import Enum
from sqlalchemy import exists, and_, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.main_db import admin_crud
from database.main_db.database import Session

from model.main_db.admin import Admin
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.chat import Chat
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.teacher_group import association_teacher_to_group
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student_ban import StudentBan

import utils.homework_utils as utils

from model.pydantic.queue_in_raw import QueueInRaw
from model.queue_db.queue_in import QueueIn
from testing_tools.logger.report_model import LabReport


class UserEnum(Enum):
    """
        Класс, описывающий всевозможные типы Telegram пользователей
    """
    Admin = 0
    Teacher = 1
    Student = 2
    Unknown = 3


async def user_verification(telegram_id: int) -> UserEnum:
    """
        Аутентификация Telegram пользователя
        Параметры:
        telegram_id (int): Telegram ID пользователя.
    """
    session: AsyncSession
    async with Session() as session:
        # проверка на админа
        user: Admin = await session.get(Admin, telegram_id)
        if user is not None:
            return UserEnum.Admin

        # проверка на препода
        user: Teacher = await session.get(Teacher, telegram_id)
        if user is not None:
            return UserEnum.Teacher

        # проверка на студента
        user: Student = await session.get(Student, telegram_id)
        if user is not None:
            return UserEnum.Student

    # неизвестный пользователь
    return UserEnum.Unknown


async def get_chats() -> list[int]:
    """Получение списка с идентифкаторами Tg-чатов

    Returns:
        list[int]: список с идентифкаторами Tg-чатов
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Chat))
        chats: list[Chat] = res.scalars().all()
        return [it.chat_id for it in chats]


async def get_group_disciplines(group_id: int) -> list[Discipline]:
    """
        Возвращает список дисциплин для учебной группы.
        Параметры:
        group_id (int): ID учебной группы
    """
    session: AsyncSession
    async with Session() as session:
        group: Group = await session.get(Group, group_id)
        return group.disciplines


async def ban_student(telegram_id: int) -> None:
    """
    Функция для записи идентификатора студента в бан-лист

    :param telegram_id: телеграм id студента

    :return: None
    """
    session: AsyncSession
    async with Session() as session:
        session.add(StudentBan(telegram_id=telegram_id))
        await session.commit()


async def unban_student(telegram_id: int) -> None:
    """
    Функция для удаления идентификатора студента из бан-листа

    :param telegram_id: телеграм id студента

    :return: None
    """
    session: AsyncSession
    async with Session() as session:
        smt = delete(StudentBan).where(
            StudentBan.telegram_id == telegram_id
        )
        await session.execute(smt)
        await session.commit()


async def is_ban(telegram_id: int) -> bool:
    """
    Функция проверки нахождения студента в бан-листе

    :param telegram_id: телеграм id студента

    :return: True, если студент забанен, иначе False
    """
    session: AsyncSession
    async with Session() as session:
        student: StudentBan = await session.get(StudentBan, telegram_id)
        return student is not None


async def get_ban_students(teacher_telegram_id: int) -> list[Student]:
    """
    Функция запроса списка забаненных студентов в группах, где
    ведет конкретный преподаватель или всех студентов, если
    запрос производится в режиме администратора

    :param teacher_telegram_id: телеграм id препода/админа

    :return: список забаненных студентов
    """
    session: AsyncSession
    async with Session() as session:
        if await admin_crud.is_admin_no_teacher_mode(teacher_telegram_id):
            smt = select(Student).where(
                exists().where(StudentBan.telegram_id == Student.telegram_id)
            )
            res = await session.execute(smt)
            return res.scalars().all()
        else:
            smt = select(Student).where(
                exists().where(StudentBan.telegram_id == Student.telegram_id)
            ).join(
                Group,
                Student.group_id == Group.id
            ).join(
                association_teacher_to_group,
                association_teacher_to_group.c.group_id == Group.id
            ).join(
                Teacher,
                association_teacher_to_group.c.teacher_id == Teacher.id
            ).where(
                Teacher.telegram_id == teacher_telegram_id
            )
            res = await session.execute(smt)
            return res.scalars().all()


async def get_students_from_group_for_ban(group_id: int) -> list[Student]:
    """
    Функция запроса студентов группы, которых можно забанить

    :param group_id: идетификатор группы

    :return: список студентов
    """
    session: AsyncSession
    async with Session() as session:
        smt = select(Student).where(
            and_(
                Student.group_id == group_id,
                Student.telegram_id.is_not(None),
                ~exists().where(
                    StudentBan.telegram_id == Student.telegram_id
                )
            )
        )
        res = await session.execute(smt)
        students: list[Student] = res.scalars().all()
        return students


async def get_students_from_group(group_id) -> list[Student]:
    """
    Функция запроса списка студентов из конкретной группы

    :param group_id: идентификатор группы

    :return: список студентов
    """
    session: AsyncSession
    async with Session() as session:
        smt = select(Student).where(Student.group_id == group_id)
        res = await session.execute(smt)
        students: list[Student] = res.scalars().all()
        return students


async def get_group(group_id: int) -> Group:
    """Возвращает учебную группу по ее ID

    Args:
        group_id (int): ID группы.

    Returns:
        Group: учебная группа с ID = group_id.
    """
    session: AsyncSession
    async with Session() as session:
        group: Group = await session.get(Group, group_id)
        return group


async def get_discipline(discipline_id: int) -> Discipline:
    """Возвращает дисциплину по ее ID.

    Args:
        discipline_id (int): ID дисциплины.

    Returns:
        Discipline: дисциплина с ID = discipline_id.
    """
    session: AsyncSession
    async with Session() as session:
        d: Discipline = await session.get(Discipline, discipline_id)
        return d


async def get_student_discipline_answer(
    student_id: int, discipline_id: int
) -> AssignedDiscipline:
    """Возвращает назначенную дисциплину для студента
    с результатами по выполнению лабораторных работ.

    Args:
        student_id (int): ID студента.
        discipline_id (int): ID дисциплины.

    Returns:
        AssignedDiscipline: назначенная дисциплина.
    """
    session: AsyncSession
    async with Session() as session:
        smt = select(AssignedDiscipline).where(
            and_(
                AssignedDiscipline.student_id == student_id,
                AssignedDiscipline.discipline_id == discipline_id
            )
        )
        res = await session.execute(smt)
        return res.scalars().first()


async def get_student_from_id(student_id: int) -> Student:
    """Функция вовзращает студента по его ID.

    Args:
        student_id (int): ID студента.

    Returns:
        Student: запись из таблицы Student.
    """
    session: AsyncSession
    async with Session() as session:
        student = await session.get(Student, student_id)
        return student


async def write_test_result(
    lab_report: LabReport, input_record: QueueIn
) -> None:
    """
    Функция записи результата тестирования заданий из л/р или домашки с
    расчетом заработанных балов по выполнению работы. Если успевает
    до деллайнов, то все норм. Иначе баллы срезаются в 2 раза.

    :param lab_report: отчет по результатам тестирования заданий работы
    :param input_record: исходные данные, отправляемые на тестирование

    :return: None
    """
    session: AsyncSession
    async with Session() as session:
        task_raw = QueueInRaw(**json.loads(input_record.data))
        smt = select(Student).where(
            Student.telegram_id == input_record.telegram_id
        )
        res = await session.execute(smt)

        student: Student = res.scalars().first()

        res = await session.execute(
            select(AssignedDiscipline).where(
                and_(
                    AssignedDiscipline.student_id == student.id,
                    AssignedDiscipline.discipline_id == task_raw.discipline_id
                )
            )
        )

        assign_discipline: AssignedDiscipline = res.scalars.first()

        hwork = utils.homeworks_from_json(assign_discipline.home_work)

        lab = None
        for it in hwork.home_works:
            if lab_report.lab_id == it.number:
                lab = it
                break

        task_done = 0
        for task in lab.tasks:
            task_done += 1 if task.is_done else 0
            for task_result in lab_report.tasks:
                if task.number == task_result.task_id:
                    task.amount_tries += 1
                    task.last_try_time = task_result.time
                    if not task.is_done and task_result.status:
                        task.is_done = True
                        task_done += 1

        lab.tasks_completed = task_done

        too_slow = False
        if (task_done == len(lab.tasks)) and not lab.is_done:
            end_time = datetime.now()
            lab.end_time = end_time
            lab.is_done = True
            if lab.deadline < end_time.date():
                too_slow = True

            discipline: Discipline = await session.get(
                Discipline, assign_discipline.discipline_id
            )

            scale_point = 100.0 / discipline.max_tasks
            lab_points = (task_done * scale_point)
            if too_slow:
                lab_points *= 0.5

            assign_discipline.point += lab_points

        assign_discipline.home_work = utils.homeworks_to_json(hwork)
        await session.commit()
        await session.close()
