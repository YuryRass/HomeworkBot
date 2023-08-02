from aiogram.types import Message
from aiogram.filters import BaseFilter
from database.main_db import admin_crud, teacher_crud, \
    student_crud

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return admin_crud.is_admin_no_teacher_mode(message.from_user.id)


class IsStudent(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return student_crud.is_student(Message.from_user.id)

class IsTeacher(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return teacher_crud.is_teacher(message.from_user.id)
