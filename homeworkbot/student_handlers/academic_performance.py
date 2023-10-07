"""Модуль позволяет получить для студента интерактивный отчет об его успеваемости
"""
import asyncio

from aiogram.types import CallbackQuery

from database.main_db import student_crud
from model.pydantic.student_report import StudentReport
from reports.interactive_report_builder import run_interactive_report_builder
from homeworkbot.routers import student_router


@student_router.callback_query(lambda call: 'academicPerf_' in call.data)
async def callback_academic_performance(call: CallbackQuery):
    """Обработчик коллбэка на создание интерактивн. отчета об успеваемости студента

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'academicPerf':
            discipline_id = int(call.data.split('_')[1])
            student = await student_crud.get_student_by_tg_id(
                call.from_user.id
            )
            await __create_report(call, student.id, discipline_id)
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных",
            )


async def __create_report(
        call: CallbackQuery,
        student_id: int,
        discipline_id: int) -> None:
    """Ассинхронная функция по созданию отчета об успеваемости студента.

    Args:
        call (CallbackQuery): коллбэк.
        student_id (int): ID студента.
        discipline_id (int): ID дисциплины.
    """
    await call.message.edit_text(text="Начинаем формировать отчет")

    # Создаем отчет об успеваемости конкретного студента
    report = await asyncio.gather(
        run_interactive_report_builder(
            student_id, discipline_id
        )
    )

    student_report: StudentReport = report[0]
    text_report = f'<i>Студент</i>: <b>{student_report.full_name}</b>\n' + \
        f'<i>Кол-во баллов</i>: {student_report.points}\n' + \
        f'<i>Пропущенных дедлайнов</i>: {student_report.deadlines_fails}\n' + \
        f'<i>Полностью выполнено лаб</i>: {student_report.lab_completed}\n' + \
        f'<i>Выполнено заданий</i>: {student_report.task_completed}\n' + \
        f'<i>Task ratio</i>: {student_report.task_ratio}\n'

    await call.message.edit_text(text=text_report)
