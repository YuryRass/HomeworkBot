"""
    Модуль auth_handlers.py осуществляет первичную авторизацию
    пользователя в Telegram чате.
"""

import re

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramAPIError
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.enums.chat_member_status import ChatMemberStatus

from homeworkbot.configuration import bot
from homeworkbot.admin_handlers import admin_keyboard
from homeworkbot.student_handlers import student_keyboard
from homeworkbot.teacher_handlers import create_teacher_keyboard

from homeworkbot.lexicon.auth_users import (
    bot_auth_messages, bot_auth_callbacks,
    bot_auth_errors, BotAuthUsers, BotAuthErrors
)

import database.main_db.common_crud as common_crud
import database.main_db.student_crud as student_crud
from database.main_db.common_crud import UserEnum

auth_router: Router = Router()


class AuthStates(StatesGroup):
    """
        Класс состояний для авторизации пользователя
        Атрибуты:
        full_name (State): ФИО Tg пользователя.
    """
    full_name = State()


async def is_subscribed(chat_id: int, user_id: int) -> bool:
    """
        Возвращает True, если пользователь с идентификатором = user_id
        присутствует в Telegram чате с идентификатором = chat_id
        Параметры:
        chat_id (int): Telegram ID чата (группы).
        user_id (int): Telegram ID пользователя.
    """
    try:
        # получаем информацию об участнике (пользователе) Tg-чата
        response = await bot.get_chat_member(chat_id, user_id)

        # если пользователь покинул чат
        if response.status == ChatMemberStatus.LEFT:
            return False
        # если пользователь присутсвует
        else:
            return True
    # пользователя нет в чате
    except TelegramAPIError:  # Bad Request
        return False


@auth_router.message(CommandStart())
async def process_start_command(message: Message):
    """
        Хэндлер, срабатывающий на команду '/start'
    """

    # Происходит проверка какой группе принадлежит пользователь
    # (админ, препод, студент). Если студент еще не ввел свои
    # персональные данные, то его telegram id не окажется в таблице Students.
    # В таком случае Tg-бот предложет пользователю дать согласие
    # на обработку его персональных данных. Если пользователь еще
    # не подписан на Tg-канал, то бот выведет соответсвующее сообщение,
    # чтобы пользователь подписался на канал.
    user = common_crud.user_verification(message.from_user.id)
    match user:
        case UserEnum.Admin:
            await message.answer(
                text=bot_auth_messages[BotAuthUsers.ADMIN_AUTH_ANSWER],
                reply_markup=admin_keyboard(message)
            )
        case UserEnum.Teacher:
            await message.answer(
                text=bot_auth_messages[BotAuthUsers.TEACHER_AUTH_ANSWER],
                reply_markup=create_teacher_keyboard(message)
            )
        case UserEnum.Student:
            await message.answer(
                text=bot_auth_messages[BotAuthUsers.STUDENT_AUTH_ANSWER],
                reply_markup=student_keyboard()
            )
        case _:
            chats = common_crud.get_chats()
            user_in_chat = False
            for chat_id in chats:
                user_in_chat = await is_subscribed(
                    chat_id, message.from_user.id
                )
                if user_in_chat:
                    break

            if user_in_chat:
                # создаем инлаин-кнопки | Да | Нет| для пользователя-студента
                yes_or_no_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
                yes_or_no_kb.row(
                    InlineKeyboardButton(
                        text=bot_auth_messages[
                            BotAuthUsers.STUDENT_BUTTON_YES
                        ], callback_data=bot_auth_callbacks[
                            BotAuthUsers.STUDENT_ANSWER_YES_CALLBACK
                        ]
                    ),
                    InlineKeyboardButton(
                        text=bot_auth_messages[BotAuthUsers.STUDENT_BUTTON_NO],
                        callback_data=bot_auth_callbacks[
                            BotAuthUsers.STUDENT_ANSWER_NO_CALLBACK
                        ]
                    ),
                    width=2
                )

                # запрос разрешения у студента на обработку его ПД
                await message.answer(
                    text=bot_auth_messages[
                        BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST
                    ],
                    reply_markup=yes_or_no_kb.as_markup(),
                )
            else:
                await message.answer(text=bot_auth_messages[
                    BotAuthUsers.TG_USER_NOT_IN_CHAT
                ],)


@auth_router.callback_query(
    lambda call: call.data in [
        bot_auth_callbacks[BotAuthUsers.STUDENT_ANSWER_YES_CALLBACK],
        bot_auth_callbacks[BotAuthUsers.STUDENT_ANSWER_NO_CALLBACK]
    ], StateFilter(default_state)
)
async def callback_auth_query(call: CallbackQuery, state: FSMContext):
    """
        Начальныйц этап идентификации пользователя
        после получения его согласия на это.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'start':
            # положит. ответ от tg-пользователя
            if call.data == bot_auth_callbacks[
                BotAuthUsers.STUDENT_ANSWER_YES_CALLBACK
            ]:
                # Устанавливаем состояние ожидания ввода ФИО
                await state.set_state(state=AuthStates.full_name)

                # сообщени от бота, чтобы пользователь ввел свои ФИО
                await call.message.edit_text(
                    text=bot_auth_messages[
                        BotAuthUsers.BOT_MESSAGE_FOR_INPUT_STUDENT_FULL_NAME
                    ]
                )

            # отриц. ответ от tg-пользователя
            if call.data == bot_auth_callbacks[
                BotAuthUsers.STUDENT_ANSWER_NO_CALLBACK
            ]:
                await call.message.edit_text(
                    text=bot_auth_messages[
                        BotAuthUsers.BOT_ANSWER_ON_STUDENT_DISAGREEMENT
                    ],
                )
        case _:
            # неизвестные коллбэк-данные
            await call.message.edit_text(
                text=bot_auth_errors[BotAuthErrors.UNKNOWN_CALLBACK_DATA],
            )


@auth_router.message(StateFilter(AuthStates.full_name))
async def input_full_name(message: Message, state: FSMContext):
    """
        Ввод полного имени (ФИО) студентом
        для его успешной авторизации в чате
    """

    full_name = message.text
    fio_pattern: re.Pattern = re.compile(
        r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]'
    )
    if not fio_pattern.match(full_name):
        await message.answer(
           text=bot_auth_errors[BotAuthErrors.NOT_FULL_NAME]
        )
    else:
        # если студент с такими ФИО уже есть в таблице Student,
        # то обновляем его Telegram ID
        if student_crud.has_student(full_name):
            student_crud.set_telegram_id(full_name, message.from_user.id)

            # студент успешно авторизовался:
            await message.answer(
                text=bot_auth_messages[BotAuthUsers.STUDENT_AUTH_SUCCESS],
                reply_markup=student_keyboard()
            )
            # очищаем состояние
            await state.clear()
        # некорректный ввод ФИО
        else:
            await message.answer(
                text=bot_auth_errors[BotAuthErrors.INCORECT_STUDENT_FULLNAME]
            )
