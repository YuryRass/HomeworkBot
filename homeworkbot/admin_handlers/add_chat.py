"""
    Модуль add_chat.py реализует добавление ID telegram чата
    в таблицу Chat.
"""

from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.state import default_state

from database.main_db import admin_crud
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.lexicon.add_chat import (
    BotAddChat, BotAddChatErrors, bot_messages, bot_errors
)

from homeworkbot.routers import admin_router


class AdminStates(StatesGroup):
    """
        Состояния администратора.
        Атрибуты:
        chat_id (int): идентификатор Tg чата.
    """
    chat_id = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['addchat']),
                      StateFilter(default_state))
async def handle_add_chat(message: Message, state: FSMContext):
    """Обработчик добавления ID чата в таблицу"""
    await _handle_add_chat(message, state)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['addchat']),
                      StateFilter(default_state))
async def handle_no_add_chat(message: Message):
    """Обработчик невозможности добавления ID чата в таблицу"""
    await message.answer(bot_errors[BotAddChatErrors.NO_RIGHTS])


async def _handle_add_chat(message: Message, state: FSMContext) -> None:
    """Функция установки состояния chat_id в классе AdminStates"""
    await state.set_state(state=AdminStates.chat_id)
    await message.answer(
        text=bot_messages[BotAddChat.INPUT_TG_ID]
    )


@admin_router.message(StateFilter(AdminStates.chat_id))
async def chat_correct(message: Message, state: FSMContext):
    """
        Добавление корректного ID чата в таблицу.
    """
    if not message.text.lstrip("-").isdigit():
        await message.answer(bot_errors[BotAddChatErrors.NOT_CORRECT_ID_CHAT])
    elif int(message.text) < 0:
        admin_crud.add_chat(int(message.text))
        await message.answer(bot_messages[BotAddChat.ADD_CHAT_SUCCESS])
        # очистка состояний Админа
        await state.clear()
    else:
        await message.answer(bot_errors[BotAddChatErrors.NOT_NEGATIVE_ID])
