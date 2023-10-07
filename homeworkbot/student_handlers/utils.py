"""
Вспомогательный модуль с функциями по созданию различных стартовых
или промежуточных InlineKeyboardButton
"""

from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import student_crud


async def create_student_disciplines_button(message: Message, prefix: str):
    """Функция создает инлаин-кнопки с дисциплинами, назначенные студенту.

    Args:
        message (Message): Tg сообщение.
        prefix (str): коллбэк префикс.
    """
    disciplines = await student_crud.get_assign_disciplines(message.from_user.id)
    if len(disciplines) < 1:
        await message.answer(text="В БД отсутствуют дисциплины!")
        return
    disciplines_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    disciplines_kb.row(
        *[
            InlineKeyboardButton(
                text=it.short_name,
                callback_data=f"{prefix}_{it.id}"
            )
            for it in disciplines
        ],
        width=1
    )
    await message.answer(
        text="Выберете дисциплину:",
        reply_markup=disciplines_kb.as_markup()
    )
