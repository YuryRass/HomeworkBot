import pytest

from aiogram import Dispatcher
from aiogram.types import Update, Message
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from tests.test_homeworkbot.test_admin_handlers.conftest import (
    AddChat, TelegramChat
)
from tests.test_homeworkbot.mocked_bot import MockedBot

from homeworkbot.configuration import bot as mocked_bot
from homeworkbot.admin_handlers.add_chat import (
    admin_router, AdminStates
)
from homeworkbot.lexicon.add_chat import (
    bot_messages, bot_errors, BotAddChat, BotAddChatErrors
)


class TestAddChat(AddChat):
    dispatcher: Dispatcher = Dispatcher()
    dispatcher.include_router(admin_router)
    bot: MockedBot = mocked_bot
    storage_key = StorageKey(
        user_id=TelegramChat.ADMIN_TG_ID, chat_id=TelegramChat.ID,
        bot_id=bot.id
    )

    async def _get_bot_message(self, message: Message) -> TelegramType:
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )

        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=100, message=message
            )
        )
        outgoing_message: TelegramType = self.bot.session.get_request()
        return outgoing_message

    async def _get_state(self) -> FSMContext:
        state: FSMContext = await self.dispatcher.storage.get_state(
            key=self.storage_key
        )
        return state

    @pytest.mark.asyncio
    async def test_handle_no_add_chat(self, not_admin_message: Message):

        outgoing_message: TelegramType = await self._get_bot_message(
            not_admin_message
        )

        assert outgoing_message.text == bot_errors[BotAddChatErrors.NO_RIGHTS]

        state: FSMContext = await self._get_state()

        assert state is None

    @pytest.mark.asyncio
    async def test_handle_add_chat(
        self, admin_message: Message,
        correct_id_chat_msg: Message,
        not_correct_id_chat_msg: Message,
        not_negative_id_chat_msg: Message
    ):

        outgoing_message: TelegramType = \
            await self._get_bot_message(admin_message)

        assert outgoing_message.text == bot_messages[BotAddChat.INPUT_TG_ID]

        state: FSMContext = await self._get_state()
        assert state == AdminStates.chat_id

        # Некорректный ввод телеграм ID

        outgoing_message: TelegramType = \
            await self._get_bot_message(not_correct_id_chat_msg)

        assert outgoing_message.text == \
            bot_errors[BotAddChatErrors.NOT_CORRECT_ID_CHAT]

        state: FSMContext = await self._get_state()
        assert state == AdminStates.chat_id

        # неотрицатательный ID чата

        outgoing_message: TelegramType = \
            await self._get_bot_message(not_negative_id_chat_msg)

        assert outgoing_message.text == \
            bot_errors[BotAddChatErrors.NOT_NEGATIVE_ID]

        state: FSMContext = await self._get_state()
        assert state == AdminStates.chat_id

        # Успешный ввод ID чата
        outgoing_message: TelegramType = \
            await self._get_bot_message(correct_id_chat_msg)

        assert outgoing_message.text == \
            bot_messages[BotAddChat.ADD_CHAT_SUCCESS]

        state: FSMContext = await self._get_state()
        assert state is None
