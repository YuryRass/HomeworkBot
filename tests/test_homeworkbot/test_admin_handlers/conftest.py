import datetime
import pytest
from enum import IntEnum
from aiogram.types import Message, Chat, User


class TelegramChat(IntEnum):
    ADMIN_TG_ID = 1
    NOT_ADMIN_TG_ID = 2
    ID = -42


class AddChat:
    def _messages(self, tg_user_id: int, text: str = "/addchat") -> Message:
        message: Message = Message(
            message_id=TelegramChat.ID, date=datetime.datetime.now(),
            chat=Chat(id=TelegramChat.ID, type='private', ),
            from_user=User(
                id=tg_user_id, is_bot=False,
                first_name='test_admin',
            ),
            text=text,
        )
        return message

    @pytest.fixture()
    def admin_message(self) -> Message:
        return self._messages(TelegramChat.ADMIN_TG_ID)

    @pytest.fixture()
    def not_admin_message(self) -> Message:
        return self._messages(TelegramChat.NOT_ADMIN_TG_ID)

    @pytest.fixture()
    def not_correct_id_chat_msg(self) -> Message:
        return self._messages(TelegramChat.ADMIN_TG_ID, "not_correct_id_chat")

    @pytest.fixture()
    def not_negative_id_chat_msg(self) -> Message:
        return self._messages(TelegramChat.ADMIN_TG_ID, "1234567")

    @pytest.fixture()
    def correct_id_chat_msg(self) -> Message:
        return self._messages(TelegramChat.ADMIN_TG_ID, str(TelegramChat.ID))
