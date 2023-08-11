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


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['addchat']))
async def handle_no_add_chat(message: Message):
    """Обработчик невозможности добавления ID чата в таблицу"""
    await message.answer("Нет прав доступа!!!")


async def _handle_add_chat(message: Message, state: FSMContext) -> None:
    """Функция установки состояния chat_id в классе AdminStates"""
    await state.set_state(state=AdminStates.chat_id)
    await message.answer(text="Введите telegram id добавляемого группового чата:")


@admin_router.message(StateFilter(AdminStates.chat_id))
async def chat_correct(message: Message, state: FSMContext):
    """
        Добавление корректного ID чата в таблицу.
    """
    if not message.text.lstrip("-").isdigit():
        await message.answer("Убедитесь, что вводите целое отрицательное число!")
    elif int(message.text) < 0:
        admin_crud.add_chat(int(message.text))
        await message.answer("Групповой чат успешно добавлен!")
        await state.clear() # очистка состояний Админа
    else:
        await message.answer("ID чата должен быть отрицательным числом!")