"""
    Модуль teacher_crud.py выполняет CRUD-операции с таблицей 'Teacher'
"""
from database.main_db.database import Session

from model.main_db.teacher import Teacher


def is_teacher(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID
        принадлежит преподавателю.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    with Session() as session:
        teacher = session.query(Teacher).filter(
            Teacher.telegram_id == telegram_id
        ).first()
        return teacher is not None

from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student

from model.main_db.teacher_discipline import TeacherDiscipline



def get_assign_group_discipline(teacher_tg_id: int, group_id: int) -> list[Discipline]:
    """
    Функция запроса списка дисциплин, которые числятся за преподавателем у конкретной группы

    :param teacher_tg_id: телеграм идентификатор преподавателя
    :param group_id: идентификатор группы

    :return: список дисциплин
    """
    with Session() as session:
        disciplines = session.query(Discipline).join(
            AssignedDiscipline,
            AssignedDiscipline.discipline_id == Discipline.id
        ).join(
            Student,
            Student.id == AssignedDiscipline.student_id
        ).filter(
                Student.group == group_id
        ).join(
            TeacherDiscipline,
            TeacherDiscipline.discipline_id == Discipline.id
        ).join(
            Teacher,
            Teacher.id == TeacherDiscipline.teacher_id
        ).filter(
            Teacher.telegram_id == teacher_tg_id
        ).all()

        return disciplines
    # disciplines = common_crud.get_group_disciplines(group_id)
    # with Session() as session:
    #     teacher = session.query(Teacher).filter(
    #         Teacher.telegram_id == teacher_tg_id
    #     ).first()
    #     teacher_disciplines = session.query(TeacherDiscipline).filter(
    #         TeacherDiscipline.teacher_id == teacher.id
    #     ).all()
    #     teacher_disciplines = [it.discipline_id for it in teacher_disciplines]
    #     disciplines = [it for it in disciplines if it.id in teacher_disciplines]
    #     return disciplines