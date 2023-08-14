"""Модуль реализует вспомогательные инструменты, необходимые перподу"""

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import teacher_crud
from homeworkbot import bot


async def create_teacher_groups_button(message: Message, callback_prefix: str):
    """Функция отобраажет спсиок учебных групп, которые назначены преподу.

    Args:
        message (Message): Tg сообщение.
        callback_prefix (str): префикс коллбэка.
    """
    groups = teacher_crud.get_assign_groups(message.from_user.id)

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


async def create_teacher_discipline_button(message: Message, callback_prefix: str):
    """Функция отображает список учебных дисциплин, которые ведёт препод.

    Args:
        message (Message): Tg сообщение.
        callback_prefix (str): префикс коллбэка.
    """
    disciplines = teacher_crud.get_teacher_disciplines(message.from_user.id)
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