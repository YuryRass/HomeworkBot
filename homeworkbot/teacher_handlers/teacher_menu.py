"""Модуль описывает главное меню препода.

Raises:
        TeacherException: неизвестная команда препода.
"""
from enum import Enum, auto

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.main_db import teacher_crud
from database.main_db.admin_crud import is_admin

import homeworkbot.admin_handlers.admin_menu as admin_keyboard
from homeworkbot.admin_handlers.unban_student import \
    create_unban_student_buttons
from homeworkbot.teacher_handlers.utils import \
    create_teacher_groups_button, create_teacher_discipline_button


from homeworkbot.routers import teacher_menu_router
from homeworkbot.filters import IsOnlyTeacherCommands


class TeacherException(Exception):
    ...


class TeacherCommand(Enum):
    BAN_STUDENT = auto()
    UNBAN_STUDENT = auto()
    DOWNLOAD_FULL_REPORT = auto()
    DOWNLOAD_SHORT_REPORT = auto()
    DOWNLOAD_FINISH_REPORT = auto()
    DOWNLOAD_ANSWER = auto()
    INTERACTIVE_REPORT = auto()
    SWITCH_TO_ADMIN = auto()


__teacher_commands = {
    TeacherCommand.BAN_STUDENT: 'Забанить',
    TeacherCommand.UNBAN_STUDENT: 'Разбанить',
    TeacherCommand.DOWNLOAD_ANSWER: 'Скачать ответы',
    TeacherCommand.INTERACTIVE_REPORT: 'Интерактивный отчет',
    TeacherCommand.DOWNLOAD_FULL_REPORT: 'Полный отчет',
    TeacherCommand.DOWNLOAD_SHORT_REPORT: 'Короткий отчет',
    TeacherCommand.DOWNLOAD_FINISH_REPORT: 'Итоговый отчет',
    TeacherCommand.SWITCH_TO_ADMIN: '🥷',
}


def create_teacher_keyboard(
    message: Message | None = None
) -> ReplyKeyboardMarkup:
    """Функция создает главную клавиатуру препода.

    Args:
        message (Message | None, optional): Tg сообщение. Defaults to None.

    Returns:
        ReplyKeyboardMarkup: преподская клавиатура.
    """
    menu_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    menu_kb.row(
        KeyboardButton(
            text=__teacher_commands[TeacherCommand.DOWNLOAD_ANSWER]
        ),
        KeyboardButton(
            text=__teacher_commands[TeacherCommand.DOWNLOAD_FINISH_REPORT]
        ),
        width=2
    )
    menu_kb.row(
        KeyboardButton(
            text=__teacher_commands[TeacherCommand.DOWNLOAD_FULL_REPORT]
        ),
        KeyboardButton(
            text=__teacher_commands[TeacherCommand.DOWNLOAD_SHORT_REPORT]
        ),
        width=2
    )
    menu_kb.row(
        KeyboardButton(
            text=__teacher_commands[TeacherCommand.INTERACTIVE_REPORT]
        ),
        width=1
    )

    footer_buttons = [
        KeyboardButton(text=__teacher_commands[TeacherCommand.BAN_STUDENT]),
        KeyboardButton(text=__teacher_commands[TeacherCommand.UNBAN_STUDENT]),
    ]

    if is_admin(message.from_user.id):
        footer_buttons.append(
            KeyboardButton(
                text=__teacher_commands[TeacherCommand.SWITCH_TO_ADMIN]
            )
        )
    menu_kb.row(*footer_buttons)
    return menu_kb.as_markup()


@teacher_menu_router.message(IsOnlyTeacherCommands(__teacher_commands))
async def handle_commands(message: Message, state: FSMContext):
    """Обработчик команд препода.

    Args:
        message (Message): Tg-сообщение.
    """
    await state.clear()  # убираем предыдущие состояния.

    command = get_current_teacher_command(message.text)

    match command:
        case TeacherCommand.SWITCH_TO_ADMIN:
            await switch_teacher_to_admin_menu(message)
        case TeacherCommand.DOWNLOAD_FULL_REPORT:
            await create_teacher_groups_button(message, 'fullReport')
        case TeacherCommand.DOWNLOAD_FINISH_REPORT:
            await create_teacher_groups_button(message, 'finishReport')
        case TeacherCommand.DOWNLOAD_SHORT_REPORT:
            await create_teacher_groups_button(message, 'shortReport')
        case TeacherCommand.BAN_STUDENT:
            await create_teacher_groups_button(message, 'groupBan')
        case TeacherCommand.UNBAN_STUDENT:
            await create_unban_student_buttons(message)
        case TeacherCommand.INTERACTIVE_REPORT:
            await create_teacher_groups_button(message, 'interactiveGrRep')
        case TeacherCommand.DOWNLOAD_ANSWER:
            await create_teacher_discipline_button(message, 'dowTAnswersDis')


async def switch_teacher_to_admin_menu(message: Message):
    """Переключение с меню препода на меню админа.

    Args:
        message (Message): _description_
    """

    # делаем изменение в БД
    teacher_crud.switch_teacher_mode_to_admin(message.from_user.id)

    await message.answer(
        text='Переключение в режим админа',
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=admin_keyboard.first_admin_keyboard(message),
    )


def get_current_teacher_command(command: str) -> TeacherCommand:
    """Получение преподской команды.

    Args:
        command (str): сама команда.

    Raises:
        TeacherException: Неизвестная команда.

    """
    for key, value in __teacher_commands.items():
        if value == command:
            return key
    raise TeacherException('Неизвестная команда')
