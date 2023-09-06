import pytest
from aiogram import Dispatcher
from aiogram.types import (
    Message, Update, User, ChatMemberMember, ChatMemberLeft,
)
from aiogram.methods import GetChatMember, EditMessageText, SendMessage
from aiogram.methods.base import TelegramType
from aiogram.fsm.storage.base import StorageKey

from homeworkbot.auth_handlers import is_subscribed, AuthStates
from homeworkbot.lexicon.auth_users import (
    bot_auth_messages, bot_auth_errors, BotAuthUsers, BotAuthErrors
)
from homeworkbot.admin_handlers import admin_keyboard
from homeworkbot.teacher_handlers.teacher_menu import create_teacher_keyboard
from homeworkbot.student_handlers.student_menu import student_keyboard
from homeworkbot.configuration import bot as mocked_bot
from homeworkbot.auth_handlers import auth_router

from database.main_db.admin_crud import add_chat

from tests.test_homeworkbot.conftest import (
    AuthHandlers, TelegramChat
)
from tests.test_homeworkbot.mocked_bot import MockedBot


class TestAuthHandlers(AuthHandlers):
    bot: MockedBot = mocked_bot
    dispatcher: Dispatcher = Dispatcher()
    dispatcher.include_router(auth_router)
    storage_key = StorageKey(
        user_id=TelegramChat.STUDENT_ID, chat_id=TelegramChat.ID,
        bot_id=bot.id
    )

    @pytest.mark.asyncio
    async def test_is_subscribed(self):
        # Случай, когда пользователь покинул чат:
        self.bot.add_result_for(
            method=GetChatMember,
            ok=True,
            result=ChatMemberLeft(
                user=User(
                    id=TelegramChat.STUDENT_ID, is_bot=False, first_name="User"
                ),
            )
        )
        user_in_chat: bool = await is_subscribed(
            chat_id=TelegramChat.ID, user_id=TelegramChat.STUDENT_ID
        )
        assert not user_in_chat

        # очистка
        self.bot.session.get_request()

        # Случай, когда пользователь есть в чате
        self.bot.add_result_for(
            method=GetChatMember,
            ok=True,
            result=ChatMemberMember(
                user=User(
                    id=TelegramChat.STUDENT_ID, is_bot=False, first_name="User"
                ),
            )
        )
        user_in_chat: bool = await is_subscribed(
            chat_id=TelegramChat.ID, user_id=TelegramChat.STUDENT_ID
        )
        assert user_in_chat

        self.bot.session.get_request()  # очистка

        # Случай, когда пользователя нет в чате
        self.bot.add_result_for(
            method=GetChatMember,
            ok=False,
            error_code=400  # BAD_REQUEST (TelegramAPIError)
        )
        user_in_chat: bool = await is_subscribed(
            chat_id=TelegramChat.ID, user_id=TelegramChat.USER_NOT_IN_CHAT_ID
        )

        assert not user_in_chat
        self.bot.session.get_request()  # очистка

    @pytest.mark.asyncio
    async def test_process_start_command(self, messages: tuple[Message]):
        admin_msg, teacher_msg, user_not_in_chat_msg, \
            unregistred_student_msg = messages

        # Ответ для админа
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(update_id=187, message=admin_msg)
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.ADMIN_AUTH_ANSWER]
        assert outgoing_message.reply_markup == admin_keyboard(admin_msg)

        # Ответ для препода
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(update_id=188, message=teacher_msg)
        )
        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.TEACHER_AUTH_ANSWER]
        assert outgoing_message.reply_markup == \
            create_teacher_keyboard(teacher_msg)

        # Ответ для пользователя, которого нет в чате
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=189, message=user_not_in_chat_msg
            )
        )
        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.TG_USER_NOT_IN_CHAT]

        # Теперь ответ для студента, который есть в чате,
        # но не прошел аутентификацию

        # добавляем номер чата в БД
        add_chat(TelegramChat.ID)

        # даем mocked-боту право на отправку сообщения
        self.bot.add_result_for(
            method=SendMessage,
            ok=True
        )

        # делаем студента подписанным на канал
        self.bot.add_result_for(
            method=GetChatMember,
            ok=True,
            result=ChatMemberMember(
                user=User(
                    id=TelegramChat.STUDENT_ID, is_bot=False, first_name="User"
                ),
            )
        )

        # подаем апдейт
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=190, message=unregistred_student_msg
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST]

        self.bot.session.get_request()  # очистка

    @pytest.mark.asyncio
    async def test_callback_auth_query(self, callback_students_answers):
        call_student_answer_yes, call_student_answer_no = \
            callback_students_answers

        self.bot.add_result_for(
            method=EditMessageText,
            ok=True,
        )

        # Ответ для студента, который не дал согласие
        # на обработку своих персональных данных
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=200, callback_query=call_student_answer_no
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, EditMessageText)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.BOT_ANSWER_ON_STUDENT_DISAGREEMENT]

        # Ответ для студента, который дал согласие
        # на обработку своих персональных данных

        self.bot.add_result_for(
            method=EditMessageText,
            ok=True,
        )

        self.bot.add_result_for(method=EditMessageText, ok=True)
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=202, callback_query=call_student_answer_yes
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, EditMessageText)
        assert outgoing_message.text == \
            bot_auth_messages[
                BotAuthUsers.BOT_MESSAGE_FOR_INPUT_STUDENT_FULL_NAME
            ]

        state = await self.dispatcher.fsm.storage.get_state(
            key=self.storage_key
        )
        assert state == AuthStates.full_name

    @pytest.mark.asyncio
    async def test_input_full_name(
        self, not_full_name_msg: Message, correct_full_name_msg: Message,
        incorrect_full_name_msg
    ):
        # неккоректный ввод ФИО студентом
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )

        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=52, message=not_full_name_msg,
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_errors[BotAuthErrors.NOT_FULL_NAME]

        # случай, когда ФИО студента нет в БД
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )

        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=52, message=incorrect_full_name_msg,
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_errors[BotAuthErrors.INCORECT_STUDENT_FULLNAME]

        # корректный ввод студентом
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )

        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=52, message=correct_full_name_msg,
            )
        )

        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.STUDENT_AUTH_SUCCESS]

        state = await self.dispatcher.fsm.storage.get_state(
            key=self.storage_key
        )
        assert state is None

    @pytest.mark.asyncio
    async def test_student_start_command(self, registred_student):
        # Ответ для зареганного студента
        self.bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
        await self.dispatcher.feed_update(
            bot=self.bot, update=Update(
                update_id=300, message=registred_student
            )
        )
        outgoing_message: TelegramType = self.bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.STUDENT_AUTH_ANSWER]
        assert outgoing_message.reply_markup == student_keyboard()
