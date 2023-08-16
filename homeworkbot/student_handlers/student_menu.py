"""Модуль реализует меню студента в Tg чате"""

from enum import Enum, auto

from aiogram.types import KeyboardButton, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from homeworkbot.routers import student_menu_router
from homeworkbot.filters import IsOnlyStudentCommands
from homeworkbot.student_handlers.utils import create_student_disciplines_button


class StudentException(Exception):
    ...


class StudentCommand(Enum):
    """Команды студента"""
    UPLOAD_ANSWER = auto()
    NEAREST_DEADLINE = auto
    ACADEMIC_PERFORMANCE = auto()


__student_commands = {
    StudentCommand.UPLOAD_ANSWER: "Загрузить ответ",
    StudentCommand.NEAREST_DEADLINE: "Ближайший дедлайн",
    StudentCommand.ACADEMIC_PERFORMANCE: "Успеваимость",
}


def student_keyboard() -> InlineKeyboardMarkup:
    """Возвращает инлаин-клавиатуру команд для студентов.

    Returns:
        ReplyKeyboardMarkup: _description_
    """
    student_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    student_kb.row(
        KeyboardButton(text=__student_commands[StudentCommand.UPLOAD_ANSWER]),
        width=1
    )
    student_kb.row(
        KeyboardButton(text=__student_commands[StudentCommand.NEAREST_DEADLINE]),
        KeyboardButton(text=__student_commands[StudentCommand.ACADEMIC_PERFORMANCE]),
        width=2
    )
    return student_kb.as_markup()


@student_menu_router.message(IsOnlyStudentCommands(__student_commands))
async def handle_commands(message: Message):
    """Обработчик команд студентов.

    Args:
        message (Message): Tg сообщение.
    """
    command = get_current_student_command(message.text)
    match command:
        case StudentCommand.UPLOAD_ANSWER:
            await create_student_disciplines_button(message, 'uploadAnswer')
        case StudentCommand.NEAREST_DEADLINE:
            await create_student_disciplines_button(message, 'nearestDeadline')
        case StudentCommand.ACADEMIC_PERFORMANCE:
            await create_student_disciplines_button(message, 'academicPerf')


def get_current_student_command(command: str) -> StudentCommand:
    for key, value in __student_commands.items():
        if value == command:
            return key
    raise StudentException("Неизвестная команда")