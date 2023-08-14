import asyncio

from utils.init_app import init_app

from homeworkbot import bot, dispatcher
import homeworkbot.fill_dispatcher as fill


async def main():
    # Регистриуем роутеры в диспетчере
    fill.include_routers_in_dispatcher(dispatcher)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    init_app()
    asyncio.run(main())