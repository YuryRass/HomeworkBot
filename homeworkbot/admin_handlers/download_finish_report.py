"""Модуль реализует Tg обработчики по началу построения
итогового отчета успеваемости студентов"""

from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from homeworkbot.admin_handlers.utils import create_groups_button
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.configuration import bot
from homeworkbot.routers import admin_router


@admin_router.message(IsOnlyAdmin(), Command(commands=['finishrep']),
                      StateFilter(default_state))
async def handle_download_finish_report(message: Message):
    await create_groups_button(message, 'finishReport')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['finishrep']),
                      StateFilter(default_state))
async def handle_no_download_finish_report(message: Message):
    await message.answer(text="Нет прав доступа!!!")