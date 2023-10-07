"""Модуль реализует обработчик по выводу ближайшего дедлайна для студента"""

import asyncio

from aiogram.types import CallbackQuery

from database.main_db import student_crud
from reports.deadline_report_builder import run_deadline_report_builder
from homeworkbot.routers import student_router


@student_router.callback_query(lambda call: 'nearestDeadline_' in call.data)
async def callback_nearest_deadline(call: CallbackQuery):
    """Обработчик по ближайшему дедлайну.

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'nearestDeadline':
            discipline_id = int(call.data.split('_')[1])
            student = await student_crud.get_student_by_tg_id(
                call.from_user.id
            )
            await __create_report(call, student.id, discipline_id)
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных"
            )


async def __create_report(
        call: CallbackQuery,
        student_id: int,
        discipline_id: int) -> None:

    """Отображает в Tg чате отчет о ближайшего дедлайне для студента"""
    await call.message.edit_text(text="Начинаем расчет ^_^")

    student_report = await asyncio.gather(
        run_deadline_report_builder(student_id, discipline_id)
    )

    await call.message.edit_text(text=f'<i>{student_report}</i>')
