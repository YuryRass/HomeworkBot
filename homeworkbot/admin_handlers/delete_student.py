from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.main_db import admin_crud, common_crud
from homeworkbot.admin_handlers.utils import create_groups_button, \
    create_callback_students_button
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.configuration import bot

router: Router = Router()


@router.message(IsOnlyAdmin(), Command(commands=['delstudent']))
async def handle_delete_student(message: Message):
    await create_groups_button(message, 'groupStudDel')


@router.message(IsNotOnlyAdmin(), Command(commands=['delstudent']))
async def handle_no_delete_student(message: Message):
    await message.answer(text="Нет прав доступа!!!")


@router.callback_query(lambda call: 'groupStudDel_' in call.data or 'studentDel_' in call.data)
async def callback_delete_student(call: CallbackQuery):
    """Удаление студента из основной БД.

    Args:
        call (CallbackQuery): callback.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'groupStudDel':
            group_id = int(call.data.split('_')[1])
            students = common_crud.get_students_from_group(group_id)
            await create_callback_students_button(call, students, 'studentDel', True)
        case 'studentDel':
            student_id = int(call.data.split('_')[1])
            admin_crud.delete_student(student_id)
            await call.message.edit_text(text="Студент успешно удален!")
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")