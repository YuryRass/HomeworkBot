import pytest
from aiogram import Dispatcher
from aiogram.types import (
    Message, Update, User, ChatMemberMember, ChatMemberLeft
)
from aiogram.methods import GetChatMember, EditMessageText, SendMessage
from aiogram.methods.base import TelegramType

from homeworkbot.auth_handlers import is_subscribed, AuthStates
from homeworkbot.lexicon import bot_auth_messages, BotAuthUsers
from homeworkbot.admin_handlers import admin_keyboard
from homeworkbot.teacher_handlers.teacher_menu import create_teacher_keyboard
from homeworkbot.configuration import bot
from homeworkbot.auth_handlers import auth_router

from database.main_db.admin_crud import add_chat

from tests.test_homeworkbot.conftest import (
    AuthHandlers, TelegramChat
)

dispatcher: Dispatcher = Dispatcher()
dispatcher.include_router(auth_router)


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

        # очистка
        bot.session.get_request()

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

        bot.session.get_request()  # очистка

        # TODO: протестировать еще исключение

    @pytest.mark.asyncio
    async def test_process_start_command(self, messages: tuple[Message]):
        admin_msg, teacher_msg, user_not_in_chat_msg, \
            unregistred_student_msg = messages

        # Ответ для админа
        bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
        await dispatcher.feed_update(
            bot=bot, update=Update(update_id=187, message=admin_msg)
        )

        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.ADMIN_AUTH_ANSWER]
        assert outgoing_message.reply_markup == admin_keyboard(admin_msg)

        # Ответ для препода
        bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
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
        bot.add_result_for(
            method=SendMessage,
            ok=True,
        )
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

        # делаем студента подписанным на канал
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
        assert isinstance(outgoing_message, SendMessage)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST]

        bot.session.get_request()  # очистка

    @pytest.mark.asyncio
    async def test_callback_auth_query(self, callback_students_answers):
        call_student_answer_yes, call_student_answer_no = \
            callback_students_answers

        bot.add_result_for(
            method=EditMessageText,
            ok=True,
        )

        # Ответ для студента, который не дал согласие
        # на обработку своих персональных данных
        await dispatcher.feed_update(
            bot=bot, update=Update(
                update_id=200, callback_query=call_student_answer_no
            )
        )

        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, EditMessageText)
        assert outgoing_message.text == \
            bot_auth_messages[BotAuthUsers.BOT_ANSWER_ON_STUDENT_DISAGREEMENT]

        # Ответ для студента, который дал согласие
        # на обработку своих персональных данных

        bot.add_result_for(
            method=EditMessageText,
            ok=True,
        )

        bot.add_result_for(method=EditMessageText, ok=True)
        await dispatcher.feed_update(
            bot=bot, update=Update(
                update_id=202, callback_query=call_student_answer_yes
            )
        )

        outgoing_message: TelegramType = bot.session.get_request()
        assert isinstance(outgoing_message, EditMessageText)
        assert outgoing_message.text == \
            bot_auth_messages[
                BotAuthUsers.BOT_MESSAGE_FOR_INPUT_STUDENT_FULL_NAME
            ]

    @pytest.mark.asyncio
    async def test_input_full_name(self):
        assert AuthStates.__states__ == (AuthStates.full_name,)
        assert AuthStates.__state_names__ == ("AuthStates:full_name",)
