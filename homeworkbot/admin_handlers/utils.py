from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import admin_crud
from homeworkbot import bot


async def create_teachers_button(message: Message, callback_prefix: str):
    """
        Создает инлаин клавиатуру с ФИО преподов.
        Параметры:
        message (Message): сообщение telegram пользователя.
        callback_prefix (str): префикс для значения callback_data.
    """
    teachers = admin_crud.get_teachers()
    if len(teachers) < 1:
        await message.answer(text="В БД отсутствуют преподаватели!")
        return
    teachers_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    teachers_kb.row(
        *[InlineKeyboardButton(
            text=it.full_name,
            callback_data=f'{callback_prefix}_{it.id}'
        ) for it in teachers],
        width=1
    )
    await message.answer(text="Выберите преподавателя:",
                         reply_markup=teachers_kb.as_markup())

async def start_upload_file_message(message: Message) -> Message:
    """
        Начало загрузки файла, отправленного в чат.
        Возвращает объект класса SendMessage
    """
    return await message.answer(
        text="<i>Загружаем ваш файл...</i>",
        # Отключает предварительный просмотр ссылок в сообщении
        disable_web_page_preview=True,
    )


async def finish_upload_file_message(message: Message,
                                     text: str = '<i>Файл загружен!</i>') -> None:

    """
        Завершение загрузки файла.
    """

    await message.edit_text(text=text)