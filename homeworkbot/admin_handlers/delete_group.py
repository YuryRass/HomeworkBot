from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.main_db import admin_crud
from homeworkbot.admin_handlers.utils import create_groups_button
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.configuration import bot

router: Router = Router()


@router.message(IsOnlyAdmin(), Command(commands=['delgroup']))
async def handle_delete_group(message: Message):
    await create_groups_button(message, 'groupDel')


@router.message(IsNotOnlyAdmin(), Command(commands=['delgroup']))
async def handle_no_delete_group(message: Message):
    await message.answer(text="Нет прав доступа!!!")


@router.callback_query(lambda call: 'groupDel_' in call.data)
async def callback_delete_group(call: CallbackQuery):
    """Удаление учебной группы.

    Args:
        call (CallbackQuery): callback.
    """
    group_id: int = int(call.data.split('_')[1])
    admin_crud.delete_group(group_id)
    await call.message.edit_text(text="Выбранная группа успешно удалена!")