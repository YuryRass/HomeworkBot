"""
    Модуль add_teacher.py реализует добавление данных
    о преподе в таблицу Teacher.
"""
import re
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from database.main_db import admin_crud
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router


class AdminStates(StatesGroup):
    """Состояния администратора"""
    teacher_name = State()
    teacher_tg_id = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['addteacher']),
                      StateFilter(default_state))
async def handle_add_teacher(message: Message, state: FSMContext):
    """Обработчик добавления препода в таблицу"""
    await _handle_add_teacher(message, state)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['addteacher']),
                      StateFilter(default_state))
async def handle_no_add_chat(message: Message):
    """Обработчик невозможности добавления препода в таблицу"""
    await message.answer("Нет прав доступа!!!")


async def _handle_add_teacher(message: Message, state: FSMContext) -> None:
    """Функция установки состояния teacher_name в классе AdminStates"""
    await state.set_state(state=AdminStates.teacher_name)
    await message.answer(
        text="Введите ФИО преподавателя (Например, Иванов Иван Иванович):"
    )


@admin_router.message(StateFilter(AdminStates.teacher_name))
async def teacher_name_correct(message: Message, state: FSMContext):
    """
        Проверка на ввод ФИО и в случае успеха - установка
        следующего состояния teacher_tg_id.
    """
    fio_pattern: re.Pattern = re.compile(
        r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]')
    if fio_pattern.match(message.text):
        await state.set_state(state=AdminStates.teacher_tg_id)
        await message.answer(text="Введите Telegram ID преподавателя:")
        # установка значения ФИО
        await state.update_data(teacher_name=message.text)
    else:
        await message.answer(
            text="Пожалуйста, проверьте корректность ввода ФИО!"
        )


@admin_router.message(StateFilter(AdminStates.teacher_tg_id))
async def teacher_id_correct(message: Message, state: FSMContext):
    """
        Проверка на ввод ID и в случае успеха -
        добавлене препода в таблицу.
    """
    if message.text.isdigit():
        teacher_name = await state.get_data()
        admin_crud.add_teacher(teacher_name['teacher_name'], int(message.text))
        await message.answer(text="Преподаватель успешно добавлен!")
        await state.clear()
    else:
        await message.answer(
            text="Пожалуйста, проверьте корректность ввода ID!"
        )
