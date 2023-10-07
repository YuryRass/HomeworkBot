"""Модуль формирует интерактивный отчет об успеваемости студента
по запросу преподавателя"""

import asyncio

from aiogram.types import (
    CallbackQuery, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import teacher_crud
from homeworkbot.routers import common_router
from model.pydantic.student_report import StudentReport
from reports.interactive_report_builder import run_interactive_report_builder

__report_prefix = [
    'interactiveDisRep_',
    'interactiveGrRep_',
    'interactiveStRep_',
]


def __is_interactive_prefix_callback(data: str) -> bool:
    for it in __report_prefix:
        if it in data:
            return True
    return False


@common_router.callback_query(
    lambda call: __is_interactive_prefix_callback(call.data)
)
async def callback_interactive_report(call: CallbackQuery):
    """Обработчик по созданию инетрактивного отчета об успеваемости
    студента.

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'interactiveGrRep':
            await call.message.edit_text(text="Выберете учебную группу")
            group_id = int(call.data.split('_')[1])
            disciplines = await teacher_crud.get_assign_group_discipline(
                call.from_user.id,
                group_id
            )
            if len(disciplines) == 0:
                await call.message.edit_text(
                    text="За группой не числится дисциплин"
                )
            else:
                disciplines_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
                disciplines_kb.row(
                    *[InlineKeyboardButton(
                        text=it.short_name,
                        callback_data=f'interactiveDisRep_{group_id}_{it.id}'
                    ) for it in disciplines],
                    width=1
                )
                await call.message.edit_text(
                    text="Выберите дисциплину:",
                    reply_markup=disciplines_kb.as_markup()
                )
        case 'interactiveDisRep':
            group_id = int(call.data.split('_')[1])
            discipline_id = int(call.data.split('_')[2])
            students = await teacher_crud.get_auth_students(group_id)
            if len(students) < 1:
                await call.message.edit_text(
                    text="В группе нет авторизованных студентов"
                )
                return
            students_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
            students_kb.row(
                *[InlineKeyboardButton(
                    text=it.full_name,
                    callback_data=f'interactiveStRep_{it.id}_{discipline_id}'
                ) for it in students],
                width=1
            )
            await call.message.edit_text(
                text="Выберите студента:",
                reply_markup=students_kb.as_markup(),
            )
        case 'interactiveStRep':
            student_id = int(call.data.split('_')[1])
            discipline_id = int(call.data.split('_')[2])
            await __create_report(call, student_id, discipline_id)
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных",
            )


async def __create_report(
        call: CallbackQuery,
        student_id: int,
        discipline_id: int) -> None:
    """Функция отображает отчет об успеваемости студента.

    Args:
        call (CallbackQuery): коллбэк.
        student_id (int): ID студента.
        discipline_id (int): ID дисциплины.
    """
    await call.message.edit_text(
        text="Начинаем формировать отчет"
    )

    report = await asyncio.gather(
        run_interactive_report_builder(student_id, discipline_id)
    )

    student_report: StudentReport = report[0]

    text_report = \
        f'<i>Студент</i>: <b>{student_report.full_name}</b>\n' + \
        f'<i>Кол-во баллов</i>: {student_report.points}\n' + \
        f'<i>Пропущенных дедлайнов</i>: {student_report.deadlines_fails}\n' + \
        f'<i>Полностью выполнено лаб</i>: {student_report.lab_completed}\n' + \
        f'<i>Выполнено заданий</i>: {student_report.task_completed}\n' + \
        f'<i>Task ratio</i>: {student_report.task_ratio}\n'

    await call.message.edit_text(text=text_report)
