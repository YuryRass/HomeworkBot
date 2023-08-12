"""
Модуль обработки команды администратора на загрузку тестов к
выбранной дисциплине
"""

from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery, ContentType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter

from homeworkbot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message
from homeworkbot.configuration import bot
from homeworkbot.routers import admin_router
from homeworkbot.filters import IsNotOnlyAdmin, IsOnlyAdmin
from database.main_db import admin_crud
from utils.unzip_test_files import save_test_files, DeleteFileException


class AdminState(StatesGroup):
    upload_test = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['uptest']),
                      StateFilter(default_state))
async def handle_upload_tests(message: Message):
    await _handle_upload_tests(message)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['uptest']),
                      StateFilter(default_state))
async def handle_no_upload_tests(message: Message):
    await message.answer(text="Нет прав доступа!!!")


async def _handle_upload_tests(message: Message):
    """Обработчик по выбору дисциплины.

    Args:
        message (Message): сообщение Tg пользователя.
    """
    # список всех дисциплин
    disciplines = admin_crud.get_all_disciplines()
    if len(disciplines) < 1:
        await message.answer(text="В БД отсутствуют данные по дисциплинам!")
        return
    disciplines_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    disciplines_kb.row(
        *[InlineKeyboardButton(
            text=it.short_name,
            callback_data=f'upTest_{it.id}'
        ) for it in disciplines],
        width=1
    )
    await message.answer(text="Выберите дисциплину для загрузки тестов:",
                         reply_markup=disciplines_kb.as_markup())


@admin_router.callback_query(lambda call: 'upTest_' in call.data)
async def callback_upload_tests(call: CallbackQuery, state: FSMContext):
    """Обработчик на callback-данные по загрузке тестов.

    Args:
        call (CallbackQuery): callback.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'upTest':
            await call.message.edit_text(text="Загрузите архив с тестами")
            # устанавливаем состояние по загрузке тестов
            # и загружаем данные - ID дисциплины.
            await state.set_state(state=AdminState.upload_test)
            await state.update_data(id=int(call.data.split('_')[1]))
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")


@admin_router.message(StateFilter(AdminState.upload_test), F.content_type == ContentType.DOCUMENT)
async def handle_upload_zip_tests(message: Message, state: FSMContext):
    """Обработчик по загрузке архива с тестами.

    Args:
        message (Message): сообщение Tg-пользователя.

    Errors:
        DeleteFileException: ошибка в удалении файла.
    """
    # начальное сообщение по загрузке...
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name
    if file_name[-4:] == ".zip":
        discipline = await state.get_data()
        discipline_id: int = discipline["id"]

        # загружаем файл с тестами (в байтах)
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        # сохраняем файлы с тестами
        discipline = admin_crud.get_discipline(discipline_id)
        discipline_path_to_test: str = discipline.path_to_test
        try:
            await save_test_files(discipline_path_to_test, downloaded_file.read())

            # сообщение о загрузке тестов
            await finish_upload_file_message(
                result_message,
                f'<i>Тесты по дисциплине "{discipline.short_name}" загружены!</i>'
            )
            await state.clear()

        except DeleteFileException as ex:
            await message.answer(text=str(ex))
    else:
        await message.answer(text="Неверный тип файла")