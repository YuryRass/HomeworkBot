"""
Модуль запуска телеграм-бота в отдельном процессе
Example:
    $ python run_bot.py
"""

import asyncio

from utils.init_app import init_app

from homeworkbot import bot, dispatcher
import homeworkbot.fill_dispatcher as fill

from testing_tools.answer.answer_processing import AnswerProcessing


async def main():
    # Регистриуем роутеры в диспетчере
    fill.include_routers_in_dispatcher(dispatcher)

    # Пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    await init_app()  # create databases

    # запускаем polling и систему проверки тестов в конкурентном режиме
    await asyncio.gather(
        dispatcher.start_polling(bot),
        AnswerProcessing(bot).run()
    )

if __name__ == '__main__':
    asyncio.run(main())
