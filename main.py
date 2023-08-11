import asyncio

from utils.init_app import init_app
from homeworkbot import bot, dispatcher, auth_handlers
from homeworkbot.admin_handlers import admin_menu



async def main():
    # Регистриуем роутер для аутентификации Tg пользователя
    dispatcher.include_router(auth_handlers.router)

    # Регистрируем роутеры админа
    dispatcher.include_router(admin_menu.admin_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    init_app()
    asyncio.run(main())