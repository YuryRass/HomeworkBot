from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from homeworkbot.admin_handlers.utils import create_teachers_button
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router

from database.main_db import admin_crud


@admin_router.message(IsOnlyAdmin(), Command(commands=['delteacher']),
                      StateFilter(default_state))
async def handle_delete_teacher(message: Message):
    await create_teachers_button(message, 'delTeacher')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['delteacher']),
                      StateFilter(default_state))
async def handle_no_delete_teacher(message: Message):
    await message.answer(text="Нет прав доступа!!!")


@admin_router.callback_query(lambda call: 'delTeacher_' in call.data)
async def callback_delete_teacher(call: CallbackQuery):
    """Удаление препода из основной БД.

    Args:
        call (CallbackQuery): callback.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'delTeacher':
            teacher_id = int(call.data.split('_')[1])
            await admin_crud.delete_teacher(teacher_id)
            await call.message.edit_text(text="Преподаватель успешно удален")
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")
