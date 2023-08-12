import json
from pathlib import Path

from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter

from database.main_db import admin_crud
from database.main_db.crud_exceptions import (
    DisciplineNotFoundException, GroupAlreadyExistException,
    DisciplineAlreadyExistException, GroupNotFoundException
)

from homeworkbot.routers import admin_router
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.configuration import bot
from homeworkbot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message

from model.pydantic.db_start_data import DbStartData


class AdminStates(StatesGroup):
    upload_config = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['upconfig']))
async def handle_upload_start_configuration(message: Message):
    await _handle_upload_start_configuration(message)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['upconfig']))
async def handle_no_upload_start_configuration(message: Message):
    await message.answer(text="Нет прав доступа!!!")


async def _handle_upload_start_configuration(message: Message, state: FSMContext):
    await message.answer(text="Загрузите json-файл для  наполнения БД")
    await state.set_state(state=AdminStates.upload_config)


@admin_router.message(StateFilter(AdminStates.upload_config),
                      F.content_type == ContentType.DOCUMENT)
async def handle_upload_discipline(message: Message, state: FSMContext):
    """Обработчик по загрузке JSON файла со стартовой инициализацией БД

    Args:
        message (Message): Tg-сообщение.

        state (FSMContext): состояние.
    """
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name

    # проверка расширения файла
    if file_name[-5:] == ".json":
        try:
            # получение информации о JSON файле и его загрузка
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)

            # получение данных из JSON файла
            data = json.loads(downloaded_file.read())
            db_start_data = DbStartData(**data)

            # инициализация БД
            admin_crud.remote_start_db_fill(db_start_data)

            # создание директорий с тестами и ответами студентов
            path = Path.cwd()
            for discipline in db_start_data.disciplines:
                Path(path.joinpath(discipline.path_to_test)).mkdir(parents=True, exist_ok=True)
                Path(path.joinpath(discipline.path_to_answer)).mkdir(parents=True, exist_ok=True)

            # сообщение о завершении
            await finish_upload_file_message(
                result_message,
                '<i>Стартовое заполнение БД завершено!</i>'
            )

            # удаление состояния
            await state.clear()

        except DisciplineNotFoundException as dnf_ex:
            await message.answer(text=str(dnf_ex))
        except GroupAlreadyExistException as gae_ex:
            await message.answer(text=str(gae_ex))
        except DisciplineAlreadyExistException as daex:
            await message.answer(text=str(daex))
        except GroupNotFoundException as gnfex:
            await message.answer(text=str(gnfex))
    else:
        await message.answer(text="Неверный тип файла")