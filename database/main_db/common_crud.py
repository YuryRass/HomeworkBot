import json
from datetime import datetime
from enum import Enum
from sqlalchemy import exists, and_

from database.main_db import admin_crud
from database.main_db.database import Session

from model.main_db.admin import Admin
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.chat import Chat
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student_ban import StudentBan
from model.main_db.teacher_group import TeacherGroup

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


def user_verification(telegram_id: int) -> UserEnum:
    """
        Аутентификация Telegram пользователя
        Параметры:
        telegram_id (int): Telegram ID пользователя.
    """
    with Session() as session:
        # проверка на админа
        user = session.query(Admin).get(telegram_id)
        if user is not None:
            return UserEnum.Admin

        # проверка на препода
        user = session.query(Teacher).filter(
            Teacher.telegram_id == telegram_id
        ).first()
        if user is not None:
            return UserEnum.Teacher

        # проверка на студента
        user = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        if user is not None:
            return UserEnum.Student

    # неизвестный пользователь
    return UserEnum.Unknown


def get_chats() -> list[int]:
    """Получение списка с идентифкаторами Tg-чатов

    Returns:
        list[int]: список с идентифкаторами Tg-чатов
    """
    with Session() as session:
        chats = session.query(Chat).all()
        return [it.chat_id for it in chats]


def get_group_disciplines(group_id: int) -> list[Discipline]:
    """
        Возвращает список дисциплин для учебной группы.
        Параметры:
        group_id (int): ID учебной группы
    """
    with Session() as session:
        disciplines = session.query(Discipline).join(
            AssignedDiscipline,
            AssignedDiscipline.discipline_id == Discipline.id
        ).join(
            Student,
            Student.id == AssignedDiscipline.student_id
        ).filter(Student.group == group_id).all()
        return disciplines
    # with Session() as session:
    #     student = session.query(Student).filter(
    #         Student.group == group_id
    #     ).first()
    #     assigned_disciplines = session.query(AssignedDiscipline).filter(
    #         AssignedDiscipline.student_id == student.id
    #     ).all()
    #     assigned_disciplines = [it.discipline_id for it in assigned_disciplines]
    #     disciplines = session.query(Discipline).filter(
    #         Discipline.id.in_(assigned_disciplines)
    #     ).all()
    #     return disciplines


def ban_student(telegram_id: int) -> None:
    """
    Функция для записи идентификатора студента в бан-лист

    :param telegram_id: телеграм id студента

    :return: None
    """
    with Session() as session:
        session.add(StudentBan(telegram_id=telegram_id))
        session.commit()


def unban_student(telegram_id: int) -> None:
    """
    Функция для удаления идентификатора студента из бан-листа

    :param telegram_id: телеграм id студента

    :return: None
    """
    with Session() as session:
        student = session.query(StudentBan).filter(
            StudentBan.telegram_id == telegram_id
        )
        student.delete(synchronize_session='fetch')
        session.commit()


def is_ban(telegram_id: int) -> bool:
    """
    Функция проверки нахождения студента в бан-листе

    :param telegram_id: телеграм id студента

    :return: True, если студент забанен, иначе False
    """
    with Session() as session:
        tg_id = session.query(StudentBan).get(telegram_id)
        return tg_id is not None


def get_ban_students(teacher_telegram_id: int) -> list[Student]:
    """
    Функция запроса списка забаненных студентов в группах, где
    ведет конкретный преподаватель или всех студентов, если
    запрос производится в режиме администратора

    :param teacher_telegram_id: телеграм id препода/админа

    :return: список забаненных студентов
    """
    with Session() as session:
        # ban_list = session.query(StudentBan).all()
        # ban_list = [it.telegram_id for it in ban_list]
        if admin_crud.is_admin_no_teacher_mode(teacher_telegram_id):
            students = session.query(Student).filter(
                exists().where(StudentBan.telegram_id == Student.telegram_id)
            ).all()
            return students
            # students = session.query(Student).filter(
            #         Student.telegram_id.in_(ban_list)
            # ).all()
            # return students
        else:
            students = session.query(Student).filter(
                exists().where(StudentBan.telegram_id == Student.telegram_id)
            ).join(
                Group,
                Group.id == Student.group
            ).join(
                TeacherGroup,
                TeacherGroup.group_id == Group.id
            ).join(
                Teacher,
                Teacher.id == TeacherGroup.teacher_id
            ).filter(
                Teacher.telegram_id == teacher_telegram_id
            ).all()
            # teacher = session.query(Teacher).filter(Teacher.telegram_id == teacher_telegram_id).first()
            # groups = session.query(TeacherGroup).filter(TeacherGroup.teacher_id == teacher.id).all()
            # groups = [it.group_id for it in groups]
            # students = session.query(Student).filter(
            #     and_(Student.group.in_(groups),
            #          Student.telegram_id.in_(ban_list)
            #          )
            # ).all()
            return students


def get_students_from_group_for_ban(group_id: int) -> list[Student]:
    """
    Функция запроса студентов группы, которых можно забанить

    :param group_id: идетификатор группы

    :return: список студентов
    """
    with Session() as session:
        students = session.query(Student).filter(
                and_(
                    Student.group == group_id,
                    Student.telegram_id.is_not(None),
                    ~exists().where(
                        StudentBan.telegram_id == Student.telegram_id
                    )
                )
        ).all()
        return students
    # with Session() as session:
    #     ban_list = session.query(StudentBan).all()
    #     ban_list = [it.telegram_id for it in ban_list]
    #     students = session.query(Student).filter(
    #         and_(
    #             Student.group == group_id,
    #             Student.telegram_id.is_not(None),
    #             Student.telegram_id.not_in(ban_list)
    #         )
    #     ).all()
    #     return students


def get_students_from_group(group_id) -> list[Student]:
    """
    Функция запроса списка студентов из конкретной группы

    :param group_id: идентификатор группы

    :return: список студентов
    """
    with Session() as session:
        students = session.query(Student).filter(
                Student.group == group_id
        ).all()
        return students


def get_group(group_id: int) -> Group:
    """Возвращает учебную группу по ее ID

    Args:
        group_id (int): ID группы.

    Returns:
        Group: учебная группа с ID = group_id.
    """
    with Session() as session:
        return session.query(Group).get(group_id)


def get_discipline(discipline_id: int) -> Discipline:
    """Возвращает дисциплину по ее ID.

    Args:
        discipline_id (int): ID дисциплины.

    Returns:
        Discipline: дисциплина с ID = discipline_id.
    """
    with Session() as session:
        return session.query(Discipline).get(discipline_id)


def get_student_discipline_answer(
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
    with Session() as session:
        answers = session.query(AssignedDiscipline).filter(
            AssignedDiscipline.student_id == student_id,
            AssignedDiscipline.discipline_id == discipline_id
        ).first()
        return answers


def get_student_from_id(student_id: int) -> Student:
    """Функция вовзращает студента по его ID.

    Args:
        student_id (int): ID студента.

    Returns:
        Student: запись из таблицы Student.
    """
    with Session() as session:
        return session.query(Student).get(student_id)


def write_test_result(lab_report: LabReport, input_record: QueueIn) -> None:
    """
    Функция записи результата тестирования заданий из л/р или домашки с
    расчетом заработанных балов по выполнению работы. Если успевает
    до деллайнов, то все норм. Иначе баллы срезаются в 2 раза.

    :param lab_report: отчет по результатам тестирования заданий работы
    :param input_record: исходные данные, отправляемые на тестирование

    :return: None
    """
    session = Session()
    task_raw = QueueInRaw(**json.loads(input_record.data))

    student = session.query(Student).filter(
        Student.telegram_id == input_record.telegram_id
    ).first()

    assig_discipline = session.query(AssignedDiscipline).filter(
        AssignedDiscipline.student_id == student.id,
        AssignedDiscipline.discipline_id == task_raw.discipline_id
    ).first()

    hwork = utils.homeworks_from_json(assig_discipline.home_work)

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

        discipline = session.query(Discipline).get(
            assig_discipline.discipline_id
        )

        scale_point = 100.0 / discipline.max_tasks
        lab_points = (task_done * scale_point)
        if too_slow:
            lab_points *= 0.5

        assig_discipline.point += lab_points

    assig_discipline.home_work = utils.homeworks_to_json(hwork)
    session.commit()
    session.close()
