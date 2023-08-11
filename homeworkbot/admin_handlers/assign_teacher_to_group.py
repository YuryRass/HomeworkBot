from aiogram.types import (
    InlineKeyboardButton,
    Message,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from homeworkbot.admin_handlers.utils import create_teachers_button
from homeworkbot.filters import IsNotOnlyAdmin, IsOnlyAdmin
from homeworkbot.routers import admin_router

from database.main_db import admin_crud


@admin_router.message(IsOnlyAdmin(), Command(commands=['assigntgr']))
async def handle_assign_teacher_to_group(message: Message):
    """
        Обработчик создания преподских инлаин-кнопок.
    """
    await create_teachers_button(message, 'assignTeacherGR')


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['assigntgr']))
async def handle_no_assign_teacher_to_group(message: Message):
    """
        Обработчик невозможности создания преподских инлаин-кнопок.
    """
    await message.answer(text="Нет прав доступа!!!")


@admin_router.callback_query(
    lambda call: 'assignTeacherGR_' in call.data or 'assignGroupT_' in call.data
)
async def callback_assign_teacher_to_group(call: CallbackQuery):
    """
        Обработчик назначения преподу учебной группы.
        Параметры:
        call (CallbackQuery): callback с данными.
    """
    # assignTeacherGR_ либо assignGroupT_
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'assignTeacherGR':
            teacher_id = int(call.data.split('_')[1])
            # группы, не назначенные преподу с ID = teacher_id
            groups = admin_crud.get_not_assign_teacher_groups(teacher_id)
            if len(groups) < 1:
                await call.message.edit_text(
                    text="В БД отсутствуют группы, куда можно добавить студента!"
                )
                return
            # создание инлаин-кнопок с названиями групп
            groups_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
            groups_kb.row(
                *[InlineKeyboardButton(
                    text=it.group_name,
                    callback_data=f'assignGroupT_{it.id}_{teacher_id}'
                ) for it in groups],
                width=1
            )

            #bot.edit_message_text()
            await call.message.edit_text(
                text="Выберите группу, которой назначается преподаватель:",
                reply_markup=groups_kb.as_markup()
            )
        case 'assignGroupT':
            group_id = call.data.split('_')[1]
            teacher_id = call.data.split('_')[2]
            # назначаем преподу группу
            admin_crud.assign_teacher_to_group(int(teacher_id), int(group_id))
            await call.message.edit_text(text="Преподаватель назначен группе")
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")