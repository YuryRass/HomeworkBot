"""
    Модуль admin_crud.py реализует для администратора
    CRUD-операции, работающие с таблицами основной БД.
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import (
    DisciplineNotFoundException, GroupAlreadyExistException,
    DisciplineAlreadyExistException, GroupNotFoundException
)

from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student

from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup
from model.pydantic.db_start_data import DbStartData

from utils.homework_utils import create_homeworks, homeworks_to_json
from utils.disciplines_utils import (
    disciplines_works_from_json,
    disciplines_works_to_json, counting_tasks
)

from config import settings


async def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору, который не может работать в режиме препода.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    session: AsyncSession
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin is None:
            return False
        return not admin.teacher_mode


async def is_admin_with_teacher_mode(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору, который может работать в режиме препода.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    session: AsyncSession
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin is None:
            return False
        return admin.teacher_mode


async def is_admin(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит администратору.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    session: AsyncSession
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        return admin is not None


async def is_admin_and_teacher(telegram_id: int) -> bool:
    """
        Возвращает True, если Telegram ID принадлежит
        администратору и преподавателю.
        Параметры:
        telegram_id (int): идентификатор пользователя в телеграме.
    """
    _is_admin: bool = await is_admin(telegram_id)
    _is_teacher: bool = await is_teacher(telegram_id)
    return _is_admin and _is_teacher


async def add_chat(chat_id: int) -> None:
    """
        Добавление ID чата в таблицу Chat
    """
    session: AsyncSession
    async with Session() as session:
        if not await session.get(Chat, chat_id):
            session.add(Chat(chat_id=chat_id))
            await session.commit()


async def add_teacher(full_name: str, tg_id: int) -> None:
    """
        Функция добавления преподавателя.
        Параметры:
        param full_name (str): ФИО препода.
        param tg_id (int): идентификатор препода в телегераме.
    """
    session: AsyncSession
    async with Session() as session:
        session.add(Teacher(full_name=full_name, telegram_id=tg_id))
        await session.commit()


async def get_teachers() -> list[Teacher]:
    """
        Получение списка преподавателей
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Teacher))
        return res.scalars().all()


async def get_not_assign_teacher_groups(teacher_id: int) -> list[Group]:
    """
        Возвращает список групп, которые не назначены преподу.
        Параметры:
        teacher_id (int): ID препода.
    """
    session: AsyncSession
    async with Session() as session:
        # teacher: Teacher = await session.get(Teacher, teacher_id)
        res = await session.execute(
            select(Teacher).options(selectinload(Teacher.groups)).where(
                Teacher.id == teacher_id
            )
        )
        teacher = res.scalar()
        assign_group = [it.id for it in teacher.groups]
        smt = await session.execute(
            select(Group).where(
                Group.id.not_in(assign_group)
            )
        )
        return smt.scalars().all()


async def assign_teacher_to_group(teacher_id: int, group_id: int) -> None:
    """
        Назначает группу преподу.
        Параметры:
        teacher_id (int): ID препода.
        group_id (int): ID группы.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).options(selectinload(Teacher.groups)).where(
                Teacher.id == teacher_id
            )
        )
        teacher: Teacher = res.scalar()
        group: Group = await session.get(Group, group_id)
        teacher.groups.append(group)
        await session.commit()


async def get_all_groups() -> list[Group]:
    """
        Возвращает список всех учебных групп.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Group))
        return res.scalars().all()


async def add_student(full_name: str, group_id: int):
    """
        Добавляет студента в БД, заполняя
    таблицы Student и AssignedDiscipline
        Параметры:
        full_name (str): ФИО студента.
        group_id (int): ID группы.
    """

    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Group).where(Group.id == group_id)
        )

        group: Group = res.scalar()

        student = Student(
            full_name=full_name,
            group_id=group_id,
        )
        group.students.append(student)
        for discipline in group.disciplines:
            empty_homework = create_homeworks(
                disciplines_works_from_json(discipline.works)
            )

            student.homeworks.append(
                AssignedDiscipline(
                    discipline_id=discipline.id,
                    home_work=homeworks_to_json(empty_homework)
                )
            )
        await session.commit()
        await session.close()


async def add_discipline(discipline: DisciplineWorksConfig) -> None:
    """
        Добавление дисциплины в таблицу Discipline
        Параметры:
        discipline (DisciplineWorksConfig): добавляемая дисциплина.
    """
    session: AsyncSession
    async with Session() as session:
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
        await session.commit()


async def add_students_group(student_groups: list[StudentsGroup]) -> None:
    """
        Функция добавления групп студентов.
        Параметры:
        student_groups (list[StudentsGroup]): Список с параметрами групп.

        Исключения:
        DisciplineNotFoundException: дисциплина не найдена.
        GroupAlreadyExistException: если группа с таким названием
        уже существует.
    """
    session: AsyncSession
    async with Session() as session:
        async with session.begin():
            try:
                for it in student_groups:
                    group = Group(
                        group_name=it.group_name,
                        students=[
                            Student(
                                full_name=student_raw,
                                homeworks=[]
                            ) for student_raw in it.students
                        ],
                        disciplines=[]
                    )

                    for discipline in it.disciplines_short_name:
                        smt = (
                            select(Discipline).
                            # options(selectinload(Discipline.groups)).
                            where(
                                Discipline.short_name.ilike(f"%{discipline}%")
                            )
                        )
                        res = await session.execute(smt)
                        current_discipline: Discipline | None = \
                            res.scalars().first()
                        if current_discipline is None:
                            raise DisciplineNotFoundException(
                                f'{discipline} нет в БД'
                            )

                        group.disciplines.append(current_discipline)

                        empty_homework = create_homeworks(
                            disciplines_works_from_json(
                                current_discipline.works
                            )
                        )
                        for student in group.students:
                            student.homeworks.append(
                                AssignedDiscipline(
                                    discipline_id=current_discipline.id,
                                    home_work=homeworks_to_json(empty_homework)
                                )
                            )

                    session.add(group)
                    # current_discipline.groups.append(group)
                await session.commit()
            except DisciplineNotFoundException as ex:
                await session.rollback()
                raise ex
            except IntegrityError as ex:
                await session.rollback()
                raise GroupAlreadyExistException(
                    f'{ex.params} уже существует'
                )
            finally:
                await session.close()


async def assign_teacher_to_discipline(
    teacher_id: int, discipline_id: int
) -> None:
    """Функция назначает преподу дисциплину.

    Args:
        teacher_id (int): ID препода.

        discipline_id (int): ID дисциплины.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).options(
                selectinload(Teacher.disciplines)
            ).where(Teacher.id == teacher_id)
        )
        teacher: Teacher = res.scalar()
        discipline: Discipline = await session.get(Discipline, discipline_id)

        teacher.disciplines.append(discipline)
        await session.commit()


async def get_not_assign_teacher_disciplines(
    teacher_id: int
) -> list[Discipline]:
    """Получить список учебных дисциплин, не назначенных преподу.

    Args:
        teacher_id (int): ID препода.

    Returns:
        list[Discipline]: список дисциплин.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(
            select(Teacher).options(
                selectinload(Teacher.disciplines)
            ).where(Teacher.id == teacher_id)
        )
        teacher: Teacher = res.scalar()
        assign_discipline = [it.id for it in teacher.disciplines]
        smt = await session.execute(
            select(Discipline).where(
                Discipline.id.not_in(assign_discipline)
            )
        )
        not_assign_teacher_disciplines: list[Discipline] = \
            smt.scalars().all()

        return not_assign_teacher_disciplines


async def delete_group(group_id: int) -> None:
    """Осуществялет удаление учебной группы по её ID из основной БД.

    Args:
        group_id (int): ID группы.
    """
    session: AsyncSession
    async with Session() as session:
        smt = delete(Group).where(Group.id == group_id)
        await session.execute(smt)
        await session.commit()


async def delete_student(student_id: int) -> None:
    """Осуществялет удаление студента по его ID из основной БД.

    Args:
        student_id (int): ID студента.
    """
    session: AsyncSession
    async with Session() as session:
        smt = delete(Student).where(Student.id == student_id)
        await session.execute(smt)
        await session.commit()


async def delete_teacher(teacher_id: int) -> None:
    """Осуществялет удаление препода по его ID из основной БД.

    Args:
        teacher_id (int): ID препода.
    """
    session: AsyncSession
    async with Session() as session:
        smt = delete(Teacher).where(Teacher.id == teacher_id)
        await session.execute(smt)
        await session.commit()


async def get_all_disciplines() -> list[Discipline]:
    """Возвращает список всех дисциплин, которые имеются в таблице.

    Returns:
        list[Discipline]: список дисциплин.
    """
    session: AsyncSession
    async with Session() as session:
        res = await session.execute(select(Discipline))
        return res.scalars().all()


async def get_discipline(discipline_id: int) -> Discipline:
    """Возвращает дисциплину по ее ID.

    Args:
        discipline_id (int): ID дисциплины.

    Returns:
        Discipline: дисциплина.
    """
    session: AsyncSession
    async with Session() as session:
        d: Discipline = await session.get(Discipline, discipline_id)
        return d


async def remote_start_db_fill(data: DbStartData) -> None:
    """
    Функция для стартовой конфигурации системы через загрузку json-файла

    :param data: данные по предметам, студентам, группам и преподавателям,
    а также какие дисциплины кому назначены и какой преподаватель их ведет

    :raises DisciplineNotFoundException: дисциплина не найдена
    :raises DisciplineAlreadyExistException: дисциплина уже существует
    :raises GroupAlreadyExistException: если группа с таким названием
    уже существует
    :raises GroupNotFoundException: если группа с таким названием не найдена

    :return: None
    """
    session: AsyncSession
    async with Session() as session:
        async with session.begin():
            admin_default_tg = settings.DEFAULT_ADMIN
            disciplines: dict[str, Discipline] = {}
            groups: dict[str, Group] = {}

            try:
                for discipline in data.disciplines:
                    if discipline.short_name in disciplines:
                        raise DisciplineAlreadyExistException(
                            f"{discipline.short_name} дублируется"
                        )
                    dis = Discipline(
                        full_name=discipline.full_name,
                        short_name=discipline.short_name,
                        path_to_test=discipline.path_to_test,
                        path_to_answer=discipline.path_to_answer,
                        works=disciplines_works_to_json(discipline),
                        language=discipline.language,
                        max_tasks=counting_tasks(discipline),
                        max_home_works=len(discipline.works),
                        groups=[]
                    )
                    disciplines[discipline.short_name] = dis

                session.add_all(disciplines.values())
                await session.flush()

                for it in data.groups:
                    group = Group(
                        group_name=it.group_name,
                        students=[
                            Student(
                                full_name=student_raw,
                                homeworks=[]
                            )
                            for student_raw in it.students
                        ]
                    )
                    groups[it.group_name] = group

                    for name in it.disciplines_short_name:
                        if name not in disciplines:
                            raise DisciplineNotFoundException(
                                f'{name} нет в БД'
                            )

                        empty_homework = create_homeworks(
                            disciplines_works_from_json(
                                disciplines[name].works
                            )
                        )
                        disciplines[name].groups.append(
                            groups[it.group_name]
                        )

                        for student in groups[it.group_name].students:
                            student.homeworks.append(
                                AssignedDiscipline(
                                    discipline_id=disciplines[name].id,
                                    home_work=homeworks_to_json(empty_homework)
                                )
                            )

                for it in data.teachers:
                    teacher = Teacher(
                        full_name=it.full_name,
                        telegram_id=it.telegram_id,
                        groups=[],
                        disciplines=[]
                    )

                    for tgr in it.assign_groups:
                        if tgr not in groups:
                            raise GroupNotFoundException(
                                f'Группа {tgr} не найдена')
                        teacher.groups.append(groups[tgr])

                    for tdis in it.assign_disciplines:
                        if tdis not in disciplines:
                            raise DisciplineNotFoundException(
                                f'Дисциплина {tdis} не найдена'
                            )
                        teacher.disciplines.append(disciplines[tdis])

                    if it.is_admin and teacher.telegram_id != admin_default_tg:
                        session.add(
                            Admin(
                                telegram_id=teacher.telegram_id
                            )
                        )
                    session.add(teacher)

                for chat in data.chats:
                    session.add(
                        Chat(chat_id=chat)
                    )
                await session.commit()
            except DisciplineNotFoundException as ex:
                await session.rollback()
                raise ex
            except DisciplineAlreadyExistException as daex:
                await session.rollback()
                raise daex
            except GroupNotFoundException as gnfex:
                await session.rollback()
                raise gnfex
            except IntegrityError as ex:
                await session.rollback()
                raise GroupAlreadyExistException(
                    f'{ex.params[0]} уже существует')
            finally:
                await session.close()


async def switch_admin_mode_to_teacher(admin_id: int) -> None:
    """Функция переключает с режима админа на режим препода.

    Args:
        admin_id (int): ID админа.
    """
    session: AsyncSession
    async with Session() as session:
        admin = await session.get(Admin, admin_id)
        admin.teacher_mode = True
        await session.commit()
