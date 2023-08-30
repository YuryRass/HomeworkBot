import pytest
import datetime
from aiogram.types import Message, Update, Chat, User
from aiogram import Bot, Dispatcher
from unittest.mock import AsyncMock
from homeworkbot.auth_handlers import process_start_command, auth_router, is_subscribed
from homeworkbot.lexicon import bot_auth_messages, BotAuthUsers
from homeworkbot.admin_handlers import admin_keyboard
from homeworkbot.teacher_handlers.teacher_menu import create_teacher_keyboard
from database.main_db.admin_crud import add_chat

from aiogram.methods import GetChatMember, Request
from aiogram.types import ChatMember, ChatMemberOwner, ChatMemberLeft, User



from confest import AuthHandlers, TelegramChat


class TestAuthHandlers(AuthHandlers):
    @pytest.mark.asyncio
    async def test_process_start_command(
        self, messages: tuple[Message], bot: Bot, dispatcher: Dispatcher
    ):
        dispatcher.include_router(auth_router)

        admin_msg, teacher_msg, user_not_in_chat_msg, \
            unregistred_student_msg = messages

        # Ответ для админа
        result = await dispatcher.feed_update(
            bot=bot, update=Update(update_id=187, message=admin_msg)
        )
        assert result.text == bot_auth_messages[BotAuthUsers.ADMIN_AUTH_ANSWER]
        assert result.reply_markup == admin_keyboard(admin_msg)

        # Ответ для препода
        result = await dispatcher.feed_update(
            bot=bot, update=Update(update_id=188, message=teacher_msg)
        )
        assert result.text == bot_auth_messages[BotAuthUsers.TEACHER_AUTH_ANSWER]
        assert result.reply_markup == create_teacher_keyboard(teacher_msg)

        # Ответ для пользователя, которого нет в чате
        result = await dispatcher.feed_update(
            bot=bot, update=Update(update_id=189, message=user_not_in_chat_msg)
        )
        assert result.text == bot_auth_messages[BotAuthUsers.TG_USER_NOT_IN_CHAT]

        # теперь ответ для студента, который есть в чате, но не прошел аутентификацию

        # добавялем ID чата в БД
        add_chat(TelegramChat.ID)

        # делаем ложный ответ от бота для функции get_chat_member()
        # Чтобы студент с id = TelegramChat.STUDENT_ID появился в чате
        # prepare_result = bot.add_result_for(
        #     GetChatMember,
        #     ok=True,
        #     result=ChatMemberOwner(
        #         user=User(
        #             id=TelegramChat.STUDENT_ID, is_bot=False, first_name="Test"
        #         ),
        #         is_anonymous=False
        #     ),
        # )

        res = await is_subscribed(TelegramChat.ID, TelegramChat.STUDENT_ID)


        # # Ответ для незареганного студента
        result = await dispatcher.feed_update(
            bot=bot, update=Update(update_id=190, message=unregistred_student_msg)
        )

        #request = bot.session.get_request()
        #assert result.text == bot_auth_messages[BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST]
        #assert result.reply_markup == create_teacher_keyboard(teacher_msg)