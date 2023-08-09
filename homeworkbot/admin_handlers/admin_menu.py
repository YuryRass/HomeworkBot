from enum import Enum, auto

from aiogram import Router
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.main_db import admin_crud
from homeworkbot.filters import IsOnlyAdminCommands
from homeworkbot.admin_handlers.add_chat import _handle_add_chat
from homeworkbot.admin_handlers.add_teacher import _handle_add_teacher
from homeworkbot.admin_handlers.utils import create_teachers_button
from homeworkbot.admin_handlers.add_student import _handle_add_student
from homeworkbot.admin_handlers.add_discipline import _handle_add_discipline
from homeworkbot.admin_handlers.add_students_group import _handle_add_students_group
from homeworkbot.admin_handlers.utils import create_groups_button
from homeworkbot.admin_handlers.unban_student import create_unban_student_buttons

from homeworkbot import bot
router: Router = Router()


class AdminException(Exception):
    ...


class AdminCommand(Enum):
    """
        Класс, описывающий команды администратора
    """
    ADD_GROUP = auto()
    ADD_TEACHER = auto()
    ADD_STUDENT = auto()
    ADD_DISCIPLINE = auto()
    ADD_CHAT = auto()
    SET_TEACHER_TO_GROUP = auto()
    SET_TEACHER_TO_DISCIPLINE = auto()
    BAN_STUDENT = auto()
    UNBAN_STUDENT = auto()
    UPLOAD_CONFIGURATION = auto()
    UPLOAD_TESTS = auto()
    ADD_STUDENTS_GROUP = auto()
    NEXT = auto()
    BACK = auto()
    DELETE_STUDENT = auto()
    DELETE_TEACHER = auto()
    DELETE_GROUP = auto()
    DOWNLOAD_FULL_REPORT = auto()
    DOWNLOAD_SHORT_REPORT = auto()
    DOWNLOAD_FINISH_REPORT = auto()
    DOWNLOAD_ANSWER = auto()
    DOWNLOAD_ALL_ANSWER_WITH_TEST = auto()
    SWITCH_TO_TEACHER = auto()


# словарь команд администратора с их пояснениями
__admin_commands = {
    AdminCommand.UPLOAD_TESTS: 'Загрузить тесты',
    AdminCommand.UPLOAD_CONFIGURATION: 'Загрузить стартовую конфигурацию',
    AdminCommand.BAN_STUDENT: 'Забанить',
    AdminCommand.UNBAN_STUDENT: 'Разбанить',
    AdminCommand.SET_TEACHER_TO_DISCIPLINE: 'Назначить преподу дисциплину',
    AdminCommand.SET_TEACHER_TO_GROUP: 'Назначить преподу группу',
    AdminCommand.ADD_STUDENTS_GROUP: 'Доб. гр. студентов',
    AdminCommand.ADD_STUDENT: 'Добавить студента',
    AdminCommand.ADD_TEACHER: 'Добавить препода',
    AdminCommand.ADD_DISCIPLINE: 'Добавить дисциплину',
    AdminCommand.ADD_CHAT: 'Добавить чат',
    AdminCommand.NEXT: '➡',
    AdminCommand.BACK: '⬅',
    AdminCommand.DELETE_STUDENT: 'Удал. студента',
    AdminCommand.DELETE_GROUP: 'Удал. группу',
    AdminCommand.DELETE_TEACHER: 'Удал. препода',
    AdminCommand.DOWNLOAD_ANSWER: 'Скачать ответы',
    AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST: 'Скачать все ответы',
    AdminCommand.DOWNLOAD_FULL_REPORT: 'Полный отчет',
    AdminCommand.DOWNLOAD_SHORT_REPORT: 'Короткий отчет',
    AdminCommand.DOWNLOAD_FINISH_REPORT: 'Итоговый отчет',
    AdminCommand.SWITCH_TO_TEACHER: '👨‍🏫'
}


def first_admin_keyboard(message: Message) -> ReplyKeyboardMarkup:
    """
        Возвращает первоначальную клавиатуру для админа.
    """
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    btns_1: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.ADD_TEACHER]),
            KeyboardButton(text=__admin_commands[AdminCommand.ADD_CHAT])
        ]

    btns_2: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.ADD_STUDENT]),
            KeyboardButton(text=__admin_commands[AdminCommand.ADD_DISCIPLINE]),
            KeyboardButton(text=__admin_commands[AdminCommand.ADD_STUDENTS_GROUP])
        ]

    btns_3: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.SET_TEACHER_TO_DISCIPLINE]),
            KeyboardButton(text=__admin_commands[AdminCommand.SET_TEACHER_TO_GROUP])
        ]

    footer_buttons = [] # клавиши для переключения

    # если админ в то же время является и преподом, то добавляем еще
    # одну клавишу в footer_buttons для переключения в режим препода
    if admin_crud.is_teacher(message.from_user.id):
        footer_buttons.append(KeyboardButton(text=__admin_commands[AdminCommand.SWITCH_TO_TEACHER]))
    footer_buttons.append(KeyboardButton(text=__admin_commands[AdminCommand.NEXT]))
    kb_builder.row(*btns_1)
    kb_builder.row(*btns_2)
    kb_builder.row(*btns_3)
    kb_builder.row(*footer_buttons)
    return kb_builder.as_markup()


def second_admin_keyboard(message: Message | None = None) -> ReplyKeyboardMarkup:
    """
        Возвращает вторую клавиатуру для админа.
    """
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    btns_1: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.DOWNLOAD_ANSWER]),
            KeyboardButton(text=__admin_commands[AdminCommand.DOWNLOAD_FINISH_REPORT])
        ]

    btns_2: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.DOWNLOAD_FULL_REPORT]),
            KeyboardButton(text=__admin_commands[AdminCommand.DOWNLOAD_SHORT_REPORT])
        ]

    btns_3: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST]),
            KeyboardButton(text=__admin_commands[AdminCommand.BAN_STUDENT]),
            KeyboardButton(text=__admin_commands[AdminCommand.UNBAN_STUDENT])
        ]

    btns_4: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.BACK]),
            KeyboardButton(text=__admin_commands[AdminCommand.NEXT])
        ]
    kb_builder.row(*btns_1)
    kb_builder.row(*btns_2)
    kb_builder.row(*btns_3)
    kb_builder.row(*btns_4)


    return kb_builder.as_markup()


def third__admin_keyboard(message: Message | None = None) -> ReplyKeyboardMarkup:
    """
        Возвращает третью клавиатуру для админа.
    """
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    btns_1: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.DELETE_GROUP]),
            KeyboardButton(text=__admin_commands[AdminCommand.DELETE_TEACHER]),
            KeyboardButton(text=__admin_commands[AdminCommand.DELETE_STUDENT])
        ]
    btns_2: list(KeyboardButton) = \
        [
            KeyboardButton(text=__admin_commands[AdminCommand.UPLOAD_TESTS]),
            KeyboardButton(text=__admin_commands[AdminCommand.UPLOAD_CONFIGURATION])
        ]

    btns_3: list(KeyboardButton) = KeyboardButton(text=__admin_commands[AdminCommand.BACK])

    kb_builder.row(*btns_1)
    kb_builder.row(*btns_2)
    kb_builder.row(btns_3)
    return kb_builder.as_markup()


def get_current_admin_command(command: str) -> AdminCommand:
    """
        Возвращает команду админа (атрибут класса AdminCommand)
        по ее значению command.
    """
    for key, value in __admin_commands.items():
        if value == command:
            return key
    raise AdminException('Неизвестная команда')


# словарь с идентификатором администраторской клавиатуры
# (в качестве ключа принимает Teleagram ID пользователя)
__menu_index: dict[int, int] = {}

# список клавиатур админа.
__menu_list = [
    first_admin_keyboard,
    second_admin_keyboard,
    third__admin_keyboard,
]


@router.message(IsOnlyAdminCommands(__admin_commands))
async def handle_commands(message: Message, state: FSMContext):
    """
        Обработчик команд администратора.
    """

    # получаем ключ команды администратора, для которого потом
    # применяем конструкцию match
    command = get_current_admin_command(message.text)
    match command:
        case AdminCommand.ADD_CHAT:
            await _handle_add_chat(message, state)
        case AdminCommand.ADD_STUDENT:
            await _handle_add_student(message, state)
        case AdminCommand.ADD_TEACHER:
            await _handle_add_teacher(message, state)
        case AdminCommand.ADD_STUDENTS_GROUP:
            await _handle_add_students_group(message, state)
        case AdminCommand.ADD_DISCIPLINE:
            await _handle_add_discipline(message, state)
        case AdminCommand.BAN_STUDENT:
            await create_groups_button(message, 'groupBan')
        case AdminCommand.UNBAN_STUDENT:
            await create_unban_student_buttons(message)
        case AdminCommand.NEXT:
            # если Tg ID пользователя нет в списке __menu_index,
            # то устанавливаем для пользователя вторую клавиатуру
            if message.from_user.id not in __menu_index:
                __menu_index[message.from_user.id] = 1
            # в противном случае переводим его на след. клавиатуру.
            else:
                __menu_index[message.from_user.id] += 1

            # искомый индекс админской клавиатуры
            index = __menu_index[message.from_user.id]

            await message.answer(
                text="Смена меню",
                reply_markup=__menu_list[index](message),
            )
        case AdminCommand.BACK:
            # если Tg ID пользователя нет в списке __menu_index,
            # то устанавливаем для пользователя первую клавиатуру
            if message.from_user.id not in __menu_index:
                __menu_index[message.from_user.id] = 0
            # в противном случае переводим его на пред. клавиатуру.
            else:
                __menu_index[message.from_user.id] -= 1
            index = __menu_index[message.from_user.id]
            await message.answer(
                text="Смена меню",
                reply_markup=__menu_list[index](message),
            )
        case AdminCommand.SET_TEACHER_TO_GROUP:
            await create_teachers_button(message, 'assignTeacherGR')
        case AdminCommand.SET_TEACHER_TO_DISCIPLINE:
            ...
        case AdminCommand.DELETE_GROUP:
            ...
        case AdminCommand.DELETE_STUDENT:
            ...
        case AdminCommand.DELETE_TEACHER:
            ...
        case AdminCommand.UPLOAD_TESTS:
            ...
        case AdminCommand.UPLOAD_CONFIGURATION:
            ...
        case AdminCommand.SWITCH_TO_TEACHER:
            ...
        case AdminCommand.DOWNLOAD_FULL_REPORT:
            ...
        case AdminCommand.DOWNLOAD_ANSWER:
            ...
        case AdminCommand.DOWNLOAD_FINISH_REPORT:
            ...
        case AdminCommand.DOWNLOAD_SHORT_REPORT:
            ...
        case AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST:
            ...