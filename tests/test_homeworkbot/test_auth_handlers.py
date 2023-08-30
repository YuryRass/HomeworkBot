import pytest
from aiogram.types import (
    Message, Update, User, ChatMemberMember, ChatMemberLeft
)
from aiogram import Dispatcher
from homeworkbot.auth_handlers import auth_router, is_subscribed
from homeworkbot.lexicon import bot_auth_messages, BotAuthUsers
from homeworkbot.admin_handlers import admin_keyboard
from homeworkbot.teacher_handlers.teacher_menu import create_teacher_keyboard
from database.main_db.admin_crud import add_chat

from aiogram.methods import GetChatMember, SendMessage
from aiogram.methods.base import TelegramType

from tests.test_homeworkbot.conftest import AuthHandlers, TelegramChat

from homeworkbot.configuration import bot


class TestAuthHandlers(AuthHandlers):
    @pytest.mark.asyncio
    async def test_is_subscribed(self):
        # Случай, когда пользователь покинул чат:
        bot.add_result_for(
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

        # Случай, когда пользователь есть в чате
        bot.add_result_for(
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

        # TODO: протестировать еще исключение

    @pytest.mark.asyncio
    async def test_process_start_command(
        self, messages: tuple[Message], dispatcher: Dispatcher
    ):
        dispatcher.include_router(auth_router)

        admin_msg, teacher_msg, user_not_in_chat_msg, \
            unregistred_student_msg = messages

        for _ in range(3):
            bot.add_result_for(
                method=SendMessage,
                ok=True
            )
        # Ответ для админа
        await dispatcher.feed_update(
            bot=bot, update=Update(update_id=187, message=admin_msg)
        )

        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.ADMIN_AUTH_ANSWER]
        assert outgoing_message.reply_markup == admin_keyboard(admin_msg)

        # # Ответ для препода
        await dispatcher.feed_update(
            bot=bot, update=Update(update_id=188, message=teacher_msg)
        )
        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.TEACHER_AUTH_ANSWER]
        assert outgoing_message.reply_markup == \
            create_teacher_keyboard(teacher_msg)

        # Ответ для пользователя, которого нет в чате
        await dispatcher.feed_update(
            bot=bot, update=Update(update_id=189, message=user_not_in_chat_msg)
        )
        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.TG_USER_NOT_IN_CHAT]

        # Теперь ответ для студента, который есть в чате,
        # но не прошел аутентификацию

        # добавляем номер чата в БД
        add_chat(TelegramChat.ID)

        # даем mocked-боту право на отправку сообщения
        bot.add_result_for(
            method=SendMessage,
            ok=True
        )

        # подписываем студента на канал
        bot.add_result_for(
            method=GetChatMember,
            ok=True,
            result=ChatMemberMember(
                user=User(
                    id=TelegramChat.STUDENT_ID, is_bot=False, first_name="User"
                ),
            )
        )

        # подаем апдейт
        await dispatcher.feed_update(
            bot=bot, update=Update(
                update_id=190, message=unregistred_student_msg
            )
        )

        outgoing_message: TelegramType = bot.session.get_request()
        _ = bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST]
