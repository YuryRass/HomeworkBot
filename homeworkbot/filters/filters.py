"""
    Модуль filters.py реализует различные фильтры,
    которые будут применяться в роутерах.
"""
from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.filters.callback_data import CallbackData
from database.main_db import admin_crud, teacher_crud, \
    student_crud

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return admin_crud.is_admin_no_teacher_mode(message.from_user.id)

class IsOnlyAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return admin_crud.is_admin(message.from_user.id)


class IsNotOnlyAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not admin_crud.is_admin(message.from_user.id)

class IsStudent(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return student_crud.is_student(Message.from_user.id)

class IsTeacher(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return teacher_crud.is_teacher(message.from_user.id)

class IsNotTeacher(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not teacher_crud.is_teacher(message.from_user.id)

class IsOnlyAdminCommands(BaseFilter):
    def __init__(self, admin_commands: dict) -> None:
        self.admin_commands = admin_commands
    async def __call__(self, message: Message) -> bool:
        command: str = message.text
        return  admin_crud.is_admin_no_teacher_mode(message.from_user.id) \
            and command in self.admin_commands.values()


class IsOnlyTeacherCommands(BaseFilter):
    def __init__(self, teacher_commands: dict) -> None:
        self.teacher_commands = teacher_commands
    async def __call__(self, message: Message) -> bool:
        command: str = message.text
        return  (teacher_crud.is_teacher(message.from_user.id) or \
            admin_crud.is_admin_with_teacher_mode(message.from_user.id)) and \
            command in self.teacher_commands.values()


class AddStudentCallbackFactory(CallbackData,
                                prefix='StudentADD',
                                sep='_'):
    """
        Фабрика коллбэков по добавлению студента.
    """
    group_id: int # ID группы, назначенный студенту
    discipline_id: int # ID дисциплины, назначенный студенту

    # Два этапа при добавлении студента в БД:
    # 1. Добавление студента в таблицу Student.
    # 2. Загрузка дисциплины для студента.
    next_step: int