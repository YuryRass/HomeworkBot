import datetime
from enum import IntEnum
import pytest

from aiogram import Dispatcher
from aiogram.types import Message, User, Chat, CallbackQuery

from homeworkbot.lexicon import (
    bot_auth_callbacks, bot_auth_messages, BotAuthUsers
)


class TelegramChat(IntEnum):
    ADMIN_ID = 1
    TEACHER_ID = 2
    STUDENT_ID = 42
    USER_NOT_IN_CHAT_ID = 123
    ID = -42


class AuthHandlers:
    def _message(self, tg_user_id, msg_id: int = TelegramChat.ID) -> Message:
        msg: Message = Message(
            message_id=msg_id,
            date=datetime.datetime.now(),
            text="/start",
            chat=Chat(id=msg_id, type="private"),
            from_user=User(
                id=tg_user_id, is_bot=False, first_name="Test",
            ),
        )
        return msg

    @pytest.fixture()
    def messages(self) -> tuple[Message]:
        admin_msg: Message = self._message(TelegramChat.ADMIN_ID)
        teacher_msg: Message = self._message(TelegramChat.TEACHER_ID)
        user_not_in_chat_msg: Message = self._message(TelegramChat.USER_NOT_IN_CHAT_ID)
        unregistred_student_msg: Message = self._message(TelegramChat.STUDENT_ID)

        return admin_msg, teacher_msg, user_not_in_chat_msg, unregistred_student_msg

    @pytest.fixture()
    def callback_students_answers(self) -> tuple[CallbackQuery]:
        students_answers: list[str] = [
            bot_auth_callbacks[BotAuthUsers.STUDENT_ANSWER_YES_CALLBACK],
            bot_auth_callbacks[BotAuthUsers.STUDENT_ANSWER_NO_CALLBACK]
        ]

        yes_and_not_text: list[str] = [
            bot_auth_messages[BotAuthUsers.STUDENT_BUTTON_YES],
            bot_auth_messages[BotAuthUsers.STUDENT_BUTTON_NO]
        ]

        callback_students_answers: tuple[CallbackQuery] = (
            CallbackQuery(
                id='chosen',
                from_user=User(
                    id=TelegramChat.STUDENT_ID, is_bot=False, first_name="Test"
                ),
                data=data,
                chat_instance="test",
                message=Message(
                    message_id=42, date=datetime.datetime.now(),
                    text=text,
                    chat=Chat(id=TelegramChat.ID, type='private'),
                )

            ) for data, text in zip(students_answers, yes_and_not_text)
        )
        return callback_students_answers
