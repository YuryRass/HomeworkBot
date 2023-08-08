"""
    Модуль admin_crud.py выполняет CRUD-операции с таблицами
    основной базы данных.
"""
from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher

from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.teacher_group import TeacherGroup
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student
from utils.disciplines_utils import disciplines_works_from_json
from utils.homework_utils import create_homeworks, homeworks_to_json
from model.pydantic.discipline_works import DisciplineWorksConfig
from utils.disciplines_utils import disciplines_works_from_json, \
    disciplines_works_to_json, counting_tasks

def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору, который не может работать в режиме препода.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return not admin.teacher_mode


def is_admin_with_teacher_mode(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору, который может работать в режиме препода.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return admin.teacher_mode


def is_admin(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит администратору.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        return admin is not None


def is_admin_and_teacher(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору и преподавателю.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    _is_admin = is_admin(telegram_id)
    _is_teacher = is_teacher(telegram_id)
    return _is_admin and _is_teacher


def add_chat(chat_id: int) -> None:
    """
        Добавление ID чата в таблицу Chat
    """

    with Session() as session:
        session.add(Chat(chat_id=chat_id))
        session.commit()


def add_teacher(full_name: str, tg_id: int) -> None:
    """
        Функция добавления преподавателя.
        Параметры:
        param full_name (str): ФИО препода.
        param tg_id (int): идентификатор препода в телегераме.
    """
    with Session() as session:
        session.add(Teacher(full_name=full_name, telegram_id=tg_id))
        session.commit()


def get_teachers() -> list[Teacher]:
    """
        Получение списка преподавателей
    """
    with Session() as session:
        return session.query(Teacher).all()


def get_not_assign_teacher_groups(teacher_id: int) -> list[Group]:
    """
        Возвращает список групп, которые не назначены преподу.
        Параметры:
        teacher_id (int): ID препода.
    """
    with Session() as session:
        # получаем сначала список групп, которые назначены преподу
        assign_group = session.query(TeacherGroup).filter(
            TeacherGroup.teacher_id == teacher_id
        )
        assign_group = [it.group_id for it in assign_group]
        # Далее получаем список групп, которых нет в списке assign_group
        not_assign_group = session.query(Group).filter(
            Group.id.not_in(assign_group)
        ).all()
        return not_assign_group


def assign_teacher_to_group(teacher_id: int, group_id: int) -> None:
    """
        Назначает группу преподу.
        Параметры:
        teacher_id (int): ID препода.
        group_id (int): ID группы.
    """
    with Session() as session:
        session.add(TeacherGroup(teacher_id=teacher_id, group_id=group_id))
        session.commit()

def get_all_groups() -> list[Group]:
    """
        Возвращает список всех учебных групп.
    """
    with Session() as session:
        return session.query(Group).all()


def add_student(full_name: str, group_id: int, discipline_id: int):
    """
        Добавляет студента в БД, заполняя
    таблицы Student и AssignedDiscipline
        Параметры:
        full_name (str): ФИО студента.
        group_id (int): ID группы.
        discipline_id (int): ID дисциплины.
    """
    session = Session()
    # добавляем студента
    student = Student(full_name=full_name, group=group_id)
    session.add(student)
    # записываем все изменения в БД,
    # чтобы потом вытащить из нее ID добавленного студента
    session.flush()

    # получаем все данные о дисциплине по ее ID
    discipline: Discipline = session.query(Discipline).get(discipline_id)
    # получаем данные по лаб. работам для данной дисциплины
    empty_homework = create_homeworks(
        disciplines_works_from_json(discipline.works)
    )
    # заполняем таблицу AssignedDiscipline
    session.add(
        AssignedDiscipline(
            student_id=student.id,
            discipline_id=discipline_id,
            home_work=homeworks_to_json(empty_homework)
        )
    )
    # сохраняем изменения и закрываем сессию
    session.commit()
    session.close()

def add_discipline(discipline: DisciplineWorksConfig) -> None:
    """
        Добавление дисциплины в таблицу Discipline
        Параметры:
        discipline (DisciplineWorksConfig): добавляемая дисциплина.
    """
    with Session() as session:
        session.add(
            Discipline(
                full_name=discipline.full_name,
                short_name=discipline.short_name,
                path_to_test=discipline.path_to_test,
                path_to_answer=discipline.path_to_answer,
                works=disciplines_works_to_json(discipline),
                language=discipline.language,
                max_tasks=counting_tasks(discipline),
                max_home_works=len(discipline.works)
            )
        )
        session.commit()