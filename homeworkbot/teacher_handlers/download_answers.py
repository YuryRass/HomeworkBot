"""
Модуль обработки команды препода на скачивание ответов студентов
по учебным дисциплинам.
"""

import asyncio
from pathlib import Path

from aiogram.types import (
    CallbackQuery, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile

from database.main_db import teacher_crud, common_crud
from homeworkbot.configuration import bot
from homeworkbot.routers import common_router
from reports.create_answers_archive import create_answers_archive


__answer_prefix = [
    'dowTAnswersDis_',
    'dowTAnswersGr_',
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


@common_router.callback_query(
    lambda call: __is_answer_prefix_callback(call.data)
)
async def callback_download_answers(call: CallbackQuery):
    """Обработчик анализа коллбэков для загрузки ответов студентов

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        # выбор учебной группы для соответсвующей дисциплины,
        # откуда будут загружаться ответы.
        case 'dowTAnswersDis':
            discipline_id = int(call.data.split('_')[1])
            discipline = await common_crud.get_discipline(discipline_id)

            # путь до ответов студентов для указанной дисциплины
            path = Path.cwd().joinpath(discipline.path_to_answer)

            # список директорий для скачивания ответов.
            # Директории имеют названия учебных групп.
            dirs = [it for it in path.iterdir() if it.is_dir()]
            if not dirs:
                await call.message.edit_text(
                    text="Директории для скачивания ответов отсутствуют"
                )
            else:
                teacher_groups = await teacher_crud.get_assign_groups(
                    call.from_user.id
                )
                dirs = [
                    it for it in dirs if it.name in
                    [tg.group_name for tg in teacher_groups]
                ]
                if not dirs:
                    await call.message.edit_text(
                        text="Данной группе дисциплины не назначены"
                    )
                    return
                groups_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
                groups_kb.row(
                    *[InlineKeyboardButton(
                        text=it.name,
                        callback_data=f'dowTAnswersGr_{it.name}_{discipline_id}'
                    ) for it in dirs],
                    width=1
                )
                await call.message.edit_text(
                    text="Выберите группу:",
                    reply_markup=groups_kb.as_markup()
                )
        # скачивание ответов для выбранной учебной группы
        case 'dowTAnswersGr':
            group_name = call.data.split('_')[1]
            discipline_id = int(call.data.split('_')[2])
            discipline = await common_crud.get_discipline(discipline_id)

            # путь до ответов студентов для выбранной дисциплины
            path = Path.cwd().joinpath(discipline.path_to_answer)

            # добавляем к пути название учебной группы
            path = path.joinpath(group_name)

            # скачивание ответов
            await _download_answer(call, path)
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных"
            )


async def _download_answer(call: CallbackQuery, path_to_group_folder: Path):
    """Ассинхронная функция скачивания и архивирования ответов студентов.

    Args:
        call (CallbackQuery): коллбэк.

        path_to_group_folder (Path): путь до ответов
            студентов некоторой учебной группы.
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
