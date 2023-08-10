"""
    Модуль admin_crud.py выполняет CRUD-операции с таблицами
    основной базы данных.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exists, and_

from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import (
    DisciplineNotFoundException, GroupAlreadyExistException
)

from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.teacher_group import TeacherGroup
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.teacher_discipline import TeacherDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student
from utils.disciplines_utils import disciplines_works_from_json
from utils.homework_utils import create_homeworks, homeworks_to_json
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup
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


def add_students_group(student_groups: list[StudentsGroup]) -> None:
    """
        Функция добавления групп студентов.
        Параметры:
        student_groups (list[StudentsGroup]): Список с параметрами групп.

        Исключения:
        DisciplineNotFoundException: дисциплина не найдена.
        GroupAlreadyExistException: если группа с таким названием уже существует.
    """
    session = Session()
    session.begin() # начало транзакции
    try:
        for it in student_groups:
            # добавляем группы
            group = Group(group_name=it.group_name)
            session.add(group)
            session.flush()

            # добавялем студентов
            students = [Student(full_name=student_raw, group=group.id) for student_raw in it.students]
            session.add_all(students)
            session.flush()

            # заполняем таблицу AssignedDiscipline
            for discipline in it.disciplines_short_name:
                current_discipline = session.query(Discipline).filter(
                    Discipline.short_name.ilike(f"%{discipline}%")
                ).first()
                if current_discipline is None:
                    raise DisciplineNotFoundException('К сожалению, дисциплины '
                                                      f'"{discipline}" нет в БД 😒')

                empty_homework = create_homeworks(
                    disciplines_works_from_json(current_discipline.works)
                )
                session.add_all([
                    AssignedDiscipline(
                        student_id=student.id,
                        discipline_id=current_discipline.id,
                        home_work=homeworks_to_json(empty_homework)
                    ) for student in students]
                )
        session.commit() # сохраняем изменения

    except DisciplineNotFoundException as ex:
        session.rollback()
        raise ex
    except IntegrityError as ex:
        session.rollback()
        raise GroupAlreadyExistException(f'{ex.params[0]} уже существует')
    finally:
        session.close()


def assign_teacher_to_discipline(teacher_id: int, discipline_id: int) -> None:
    """Функция назначает преподу дисицплину.

    Args:
        teacher_id (int): ID препода.

        discipline_id (int): ID дисциплины.
    """

    with Session() as session:
        session.add(TeacherDiscipline(teacher_id=teacher_id, discipline_id=discipline_id))
        session.commit()

def get_not_assign_teacher_disciplines(teacher_id: int) -> list[Discipline]:
    """Получить список учебных дисциплин, не назначенных преподу.

    Args:
        teacher_id (int): ID препода.

    Returns:
        list[Discipline]: список дисциплин.
    """

    # Используем соединение LEFT JOIN
    with Session() as session:
        not_assign_teacher_disciplines = session.query(
            Discipline
        ).outerjoin(
            TeacherDiscipline
        ).filter(
            TeacherDiscipline.discipline_id.is_(None)
        ).all()

        return not_assign_teacher_disciplines
