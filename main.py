# main.py
import asyncio
from aiogram import Dispatcher

from utils.init_app import init_app
from homeworkbot import bot
from homeworkbot import auth_handlers
from homeworkbot.admin_handlers import admin_menu, add_chat, \
    add_teacher



async def main():
    # Инициализируем диспетчер
    dp: Dispatcher = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(auth_handlers.router)
    dp.include_router(admin_menu.router)
    dp.include_router(add_chat.router)
    dp.include_router(add_teacher.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    init_app()
    asyncio.run(main())