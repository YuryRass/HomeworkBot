"""
Модуль обработки команды администратора на скачивание
ответов студентов по учебным дисциплинам.
"""

import asyncio
from pathlib import Path

from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types.input_file import FSInputFile

from database.main_db import admin_crud
from homeworkbot.admin_handlers.utils import create_discipline_button
from homeworkbot.configuration import bot
from homeworkbot.routers import admin_router, common_router
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from reports.create_answers_archive import create_answers_archive


@admin_router.message(IsOnlyAdmin(), Command(commands=['granswer']),
                      StateFilter(default_state))
async def handle_download_answers(message: Message):
    await create_discipline_button(message, 'dowAnswersDis')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['granswer']),
                      StateFilter(default_state))
async def handle_no_download_answers(message: Message):
    await message.answer(text="Нет прав доступа!!!")


__answer_prefix = [
    'dowAnswersDis_',
    'dowAnswersGr_',
]


def __is_answer_prefix_callback(data: str) -> bool:
    """Функция проверки нахождения одного из префиксов
    списка __answer_prefix в строке data.

    Args:
        data (str): данные callback-а.

    Returns:
        bool: True, если префикс присутствует в данных callback-а
    """
    for it in __answer_prefix:
        if it in data:
            return True
    return False


@common_router.callback_query(lambda call: __is_answer_prefix_callback(call.data))
async def callback_download_answers(call: CallbackQuery):
    """Обработчик анализа коллбэков для загрузки ответов студентов

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        # выбор учебной группы для соответсвующей дисциплины,
        # откуда будут загружаться ответы.
        case 'dowAnswersDis':
            discipline_id = int(call.data.split('_')[1])
            discipline = admin_crud.get_discipline(discipline_id)

            # путь до ответов студентов для указанной дисциплины
            path = Path.cwd().joinpath(discipline.path_to_answer)

            # список директорий для скачивания ответов.
            # Директории имеют названия учебных групп.
            dirs = [it for it in path.iterdir() if it.is_dir()]
            if not dirs:
                await call.message.edit_text(text="Директории для скачивания ответов отсутствуют")
            else:
                groups_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
                groups_kb.row(
                    *[InlineKeyboardButton(
                        text=it.name,
                        callback_data=f'dowAnswersGr_{it.name}_{discipline_id}'
                    ) for it in dirs],
                    width=1
                )
                await call.message.edit_text(
                    text="Выберите группу:",
                    reply_markup=groups_kb.as_markup()
                )
        # скачивание ответов для выбранной учебной группы
        case 'dowAnswersGr':
            group_name = call.data.split('_')[1]
            discipline_id = int(call.data.split('_')[2])
            discipline = admin_crud.get_discipline(discipline_id)

            # путь до ответов студентов для выбранной дисциплины
            path = Path.cwd().joinpath(discipline.path_to_answer)

            # добавляем к пути название учебной группы
            path = path.joinpath(group_name)

            # скачивание ответов
            await _download_answer(call, path)
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")


async def _download_answer(call: CallbackQuery, path_to_group_folder: Path):
    """Ассинхронная функция скачивания и архивирования ответов студентов.

    Args:
        call (CallbackQuery): коллбэк.

        path_to_group_folder (Path): путь до ответов студентов некоторой учебной группы.
    """
    await call.message.edit_text(text="Начинаем формировать отчет")

    # путь до созданного архива с ответами студентов
    # Функция выполняется в отдельном потоке в неблокирующем режиме
    path_to_archive = await asyncio.gather(
        asyncio.to_thread(create_answers_archive, path_to_group_folder)
    )

    await call.message.edit_text(text="Архив успешно сформирован")

    # отправка в чат созданного архива
    await bot.send_document(
        call.message.chat.id,
        FSInputFile(path_to_archive[0])
    )
