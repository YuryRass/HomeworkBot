"""
    Модуль реализует функции по созданию и отправке
    различных сообщений в Tg чате.
"""
from aiogram.types import (
    InlineKeyboardButton,
    Message,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import admin_crud
from model.main_db.student import Student
from model.main_db.discipline import Discipline


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

    """Завершение загрузки файла"""

    await message.edit_text(text=text)


async def create_groups_button(message: Message, callback_prefix: str) -> None:
    """Создание и отображение клавиш с учебными группами.

    Args:
        message (Message): Tg сообщение.

        callback_prefix (str): начало названия коллбэка.
    """
    groups = admin_crud.get_all_groups()
    if len(groups) < 1:
        await message.answer(text="В БД отсутствуют группы!")
        return
    groups_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    groups_kb.row(
        *[InlineKeyboardButton(
            text=it.group_name,
            callback_data=f'{callback_prefix}_{it.id}'
        ) for it in groups],
        width=1
    )
    await message.answer(
        text="Выберете группу в которой учится студент:",
        reply_markup=groups_kb.as_markup()
    )


async def create_callback_students_button(
        call: CallbackQuery,
        students: list[Student],
        callback_prefix: str, id_flag: bool = False) -> None:
    """Создание инлаин-кнопок с коллбэками с ФИО студентов.

    Args:
        call (CallbackQuery): коллбэк.

        students (list[Student]): список студентов.

        callback_prefix (str): начало названия коллбэка.

        id_flag (bool, optional): флаг для инициализации callback-a,
        если False, то используем telegram_id студента,
        в противном случае - id студента в таблице Student. Defaults to False.
    """
    if len(students) < 1:
        await call.answer(text="В группе нет студентов")
        return

    # Создание инлаин-кнопок
    students_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    students_kb.row(
        *[InlineKeyboardButton(
            text=it.full_name,
            callback_data=f'{callback_prefix}_{it.telegram_id if not id_flag else it.id}'
        ) for it in students],
        width=1
    )

    # отображение клавиатуры с инлаин-кнопками - ФИО студентов
    await call.message.edit_text(
        text="Выберите студента:",
        reply_markup=students_kb.as_markup(),
    )


async def create_callback_disciplines_button(
        call: CallbackQuery,
        disciplines: list[Discipline],
        teacher_id: int,
        callback_prefix: str,) -> None:
    """Создание инлаин-кнопок с коллбэками с названиями дисциплин.

    Args:
        call (CallbackQuery): коллбэк.

        disciplines (list[Discipline]): список преподов.

        teacher_id (int): Tg ID препода.

        callback_prefix (str): начало названия коллбэка.
    """
    if len(disciplines) < 1:
        await call.answer(text="В БД отсутствуют данные по дисциплинам!!")
        return

    # Создание инлаин-кнопок
    disciplines_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    disciplines_kb.row(
        *[InlineKeyboardButton(
            text=it.short_name,
            callback_data=f'{callback_prefix}_{teacher_id}_{it.id}'
        ) for it in disciplines],
        width=1
    )

    # отображение клавиатуры с инлаин-кнопками
    await call.message.edit_text(
        text="Выберите дисциплину:",
        reply_markup=disciplines_kb.as_markup(),
    )


async def create_discipline_button(message: Message, callback_prefix: str):
    """Создает и отображает в Tg-чате список со всеми учебными дисциплинами.

    Args:
        message (Message): Tg-сообщение.
        callback_prefix (str): префикс callback-a.
    """
    disciplines = admin_crud.get_all_disciplines()
    if len(disciplines) < 1:
        await message.answer(text="В БД отсутствуют дисциплины!")
        return
    disciplines_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    disciplines_kb.row(
        *[InlineKeyboardButton(
            text=it.short_name,
            callback_data=f'{callback_prefix}_{it.id}'
        ) for it in disciplines],
        width=1
    )
    await message.answer(
        text="Выберете дисциплину:",
        reply_markup=disciplines_kb.as_markup()
    )
