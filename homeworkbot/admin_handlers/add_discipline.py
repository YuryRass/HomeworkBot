"""
    Модуль add_discipline.py добавляет учебную дисциплину
    в таблицу Discipline. Данные по учебной дисицплине
    отправляет админ в JSON формате.
"""
from pathlib import Path

from aiogram import F
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter

from homeworkbot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router
from homeworkbot.configuration import bot

from database.main_db import admin_crud
from utils.disciplines_utils import disciplines_works_from_json


class AdminStates(StatesGroup):
    """Класс состояний админа для добавления дисциплины."""
    upload_discipline = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['adddiscipline']),
                      StateFilter(default_state))
async def handle_add_discipline(message: Message, state: FSMContext):
    """Обработчик возможности добавления дисциплины."""
    await _handle_add_discipline(message, state)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['adddiscipline']),
                      StateFilter(default_state))
async def handle_no_add_discipline(message: Message):
    """
        Обработчик невозможности добавления дисциплины.
    """
    await message.answer(text="Нет прав доступа!!!")


async def _handle_add_discipline(message: Message, state: FSMContext):
    """
        Обработчик установки состояния админа для загрузки дисциплины.
    """
    await message.answer(text="Загрузите json-файл с конфигурацией дисциплины")
    await state.set_state(state=AdminStates.upload_discipline)


@admin_router.message(StateFilter(AdminStates.upload_discipline),
                F.content_type == ContentType.DOCUMENT)
async def handle_upload_discipline(message: Message, state: FSMContext):
    """
        Обработчик загрузки дисциплины и добавления ее в таблицу.
    """
    # сообщение о начале загрузки файла
    result_message = await start_upload_file_message(message)

    file_type = message.document.mime_type
    if file_type == 'application/json':
        file_info = await bot.get_file(message.document.file_id)
        # получаем экземпляр байтового потока с данными из файла
        downloaded_file = await bot.download_file(file_info.file_path)

        # загружаем данные по дисциплине и переводим их в pydantic модель
        discipline = disciplines_works_from_json(downloaded_file.read())

        # добавляем дисциплину в таблицу
        admin_crud.add_discipline(discipline)

        path = Path.cwd() # текущий рабочий каталог

        # создаем директории, где будут храниться тесты
        # и ответы студентов для загруженной дисицплины
        Path(path.joinpath(discipline.path_to_test)).mkdir(parents=True, exist_ok=True)
        Path(path.joinpath(discipline.path_to_answer)).mkdir(parents=True, exist_ok=True)

        # оповещаем о завершении загрузки файла
        await finish_upload_file_message(result_message,
                                         f'<i>Дисциплина {discipline.short_name} добавлена!</i>')

    else:
        await message.answer(text="Неверный тип файла")

    # очистка состояния админа
    await state.clear()