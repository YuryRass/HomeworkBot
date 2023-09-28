from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from database.main_db import admin_crud

from homeworkbot.admin_handlers.utils import create_groups_button
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router


@admin_router.message(IsOnlyAdmin(), Command(commands=['delgroup']),
                      StateFilter(default_state))
async def handle_delete_group(message: Message):
    await create_groups_button(message, 'groupDel')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['delgroup']),
                      StateFilter(default_state))
async def handle_no_delete_group(message: Message):
    await message.answer(text="Нет прав доступа!!!")


@admin_router.callback_query(lambda call: 'groupDel_' in call.data)
async def callback_delete_group(call: CallbackQuery):
    """Удаление учебной группы.

    Args:
        call (CallbackQuery): callback.
    """
    group_id: int = int(call.data.split('_')[1])
    admin_crud.delete_group(group_id)
    await call.message.edit_text(text="Выбранная группа успешно удалена!")
