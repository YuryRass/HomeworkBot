import asyncio

from utils.init_app import init_app

from homeworkbot import bot, dispatcher
from homeworkbot.auth_handlers import router

# инициализиация роутеров админа и препода
from homeworkbot.admin_handlers import *
from homeworkbot.teacher_handlers import *

from homeworkbot.routers import admin_menu_router, admin_router, teacher_menu_router



async def main():
    # Регистриуем роутер для аутентификации Tg пользователя
    dispatcher.include_router(router)

    # Регистрируем роутеры админа и препода в диспетчере
    dispatcher.include_router(admin_menu_router)
    dispatcher.include_router(admin_router)
    dispatcher.include_router(teacher_menu_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    init_app()
    asyncio.run(main())