"""
    Модуль реализует назначение преподавателю дисицплины
"""

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router

from homeworkbot.admin_handlers.utils import create_teachers_button, \
    create_callback_disciplines_button

from database.main_db.admin_crud import get_not_assign_teacher_disciplines, \
    assign_teacher_to_discipline

from model.main_db.discipline import Discipline


@admin_router.message(IsOnlyAdmin(), Command(commands=['assigntd']),
                      StateFilter(default_state))
async def _assign_teacher_to_discipline_handler(message: Message):
    """Обработчик на назначение дисицплины преподу.

    Args:
        message (Message): сообщение Tg пользователя.
    """
    # отображаем список преподов для выбора
    await create_teachers_button(message, 'assignTeacherDis')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['assigntd']),
                      StateFilter(default_state))
async def _not_assign_teacher_to_discipline_handler(message: Message):
    """Обработчик на невозможность назначения дисицплины преподу.

    Args:
        message (Message): сообщение Tg пользователя.
    """

    await message.answer(text='У вас нет прав доступа!!!')


@admin_router.callback_query(lambda call: 'assignTeacherDis_' in call.data
                             or 'assignDiscT_' in call.data)
async def process_assign_teacher_to_discipline(call: CallbackQuery) -> None:
    callback_type: str = call.data.split('_')[0]
    match callback_type:
        case 'assignTeacherDis':
            teacher_id: int = int(call.data.split('_')[1])
            not_assign_teacher_disciplines: list[Discipline] = \
                await get_not_assign_teacher_disciplines(teacher_id)

            # создаем и отображаем список дисциплин для назначения преподу
            await create_callback_disciplines_button(
                call, not_assign_teacher_disciplines, teacher_id, 'assignDiscT'
            )

        case 'assignDiscT':
            teacher_id: int = int(call.data.split('_')[1])
            discipline_id: int = int(call.data.split('_')[2])

            # назначаем дисциплину преподу
            await assign_teacher_to_discipline(teacher_id, discipline_id)

            await call.message.edit_text(
                text='Дисциплина назначена прподавателю'
            )

        case _:
            await call.message.edit_text(
                text='Неизвестный формат для обработки данных'
            )
