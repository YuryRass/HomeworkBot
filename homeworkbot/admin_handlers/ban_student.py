from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from database.main_db import common_crud

from homeworkbot.admin_handlers.utils import \
    create_groups_button, create_callback_students_button

from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router

@admin_router.message(IsOnlyAdmin(), Command(commands=['ban']),
                      StateFilter(default_state))
async def handle_ban_student(message: Message):
    await create_groups_button(message, 'groupBan')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['ban']),
                      StateFilter(default_state))
async def handle_no_ban_student(message: Message):
    await message.answer(text="Нет прав доступа!!!")


@admin_router.callback_query(
    lambda call: 'studentBan_' in call.data or 'groupBan_' in call.data
)
async def callback_ban_student(call: CallbackQuery):
    """Обработчик коллбэка по забаниванию студента.

    Args:
        call (CallbackQuery): сам коллбэк.
    """
    type_callback = call.data.split('_')[0] # префикс коллбэка
    match type_callback:
        case 'groupBan':
            group_id = int(call.data.split('_')[1])
            students = common_crud.get_students_from_group_for_ban(group_id)

            # отображение в Tg чате списка студентов
            await create_callback_students_button(call, students, 'studentBan')
        case 'studentBan':
            telegram_id = int(call.data.split('_')[1])
            common_crud.ban_student(telegram_id)
            await call.message.edit_text(text="Студент добавлен в бан-лист")
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")