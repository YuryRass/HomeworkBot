import asyncio
import os
import shutil
from datetime import datetime
from pathlib import Path

from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router
from homeworkbot.configuration import bot


@admin_router.message(IsOnlyAdmin(), Command(commands=['dowall']),
                      StateFilter(default_state))
async def handle_download_all_test_and_answer(message: Message):
    await _handle_download_all_test_and_answer(message)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['dowall']),
                      StateFilter(default_state))
async def handle_no_download_all_test_and_answer(message: Message):
    await message.answer(text="Нет прав доступа!!!")


async def _handle_download_all_test_and_answer(message: Message):
    """Обработчик по запуску создания архива из директории с дисциплинами,
    где хранятся данные по ответам и тесты.

    Args:
        message (Message): Tg сообщение.
    """
    await message.answer(text="Начинаем формировать отчет")

    # путь до архива, где хранятся все данные по ответам студентов и тесты
    path_to_archive = await asyncio.gather(
        asyncio.to_thread(create_archive_all_data)
    )

    await message.answer(text="Архив успешно сформирован")

    # отправка в чат архива с данными
    await bot.send_document(
        message.chat.id,
        FSInputFile(path_to_archive[0])
    )


def create_archive_all_data() -> Path:
    """
    Функция запуска создания архива из директории с дисциплинами,
    где хранятся данные по ответам и тесты.

    :return: Путь до сформированного архива.
    """
    path = Path(Path.cwd().joinpath(os.getenv("TEMP_REPORT_DIR")))
    file_name = f'data_{datetime.now().date()}'

    shutil.make_archive(
        str(path.joinpath(f'{file_name}')),
        'zip', Path.cwd().joinpath('_disciplines')
    )

    return path.joinpath(f'{file_name}.zip')