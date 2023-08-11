from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from database.main_db import common_crud
from homeworkbot.filters import IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router


@admin_router.message(IsOnlyAdmin(), Command(commands=['unban']))
async def handle_unban_student(message: Message):
    await create_unban_student_buttons(message)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['unban']))
async def handle_no_unban_student(message: Message):
    await message.answer(text="Нет прав доступа!!!")


async def create_unban_student_buttons(message: Message):
    """Создание инлаин-клавиатуры для разбанивания студентов.

    Args:
        message (Message): сообщение в Tg чате.
    """
    students = common_crud.get_ban_students(message.from_user.id)
    if len(students) < 1:
        await message.answer(text="Нет забаненных студентов!")
        return
    students_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    students_kb.row(
        *[InlineKeyboardButton(
            text=it.full_name,
            callback_data=f'studentUnBan_{it.telegram_id}'
        ) for it in students],
        width=1
    )
    await message.answer(
        text="Выберете студента:",
        reply_markup=students_kb.as_markup()
    )


@admin_router.callback_query(lambda call: 'studentUnBan_' in call.data)
async def callback_unban_student(call: CallbackQuery):
    """Обработчик коллбэка для разбанивания студента.

    Args:
        call (CallbackQuery): сам коллбэк.
    """
    type_callback = call.data.split('_')[0] # префикс коллбэка
    match type_callback:
        case 'studentUnBan':
            telegram_id = int(call.data.split('_')[1])
            common_crud.unban_student(telegram_id)
            await call.message.edit_text(text="Студент разбанен!")
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных"
            )