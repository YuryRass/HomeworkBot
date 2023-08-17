import asyncio
import os
from pathlib import Path

from utils.init_app import init_app

from homeworkbot import bot, dispatcher
import homeworkbot.fill_dispatcher as fill

from testing_tools.answer.answer_processing import AnswerProcessing
from testing_tools.checker.task_processing import TaskProcessing


async def main():
    from dotenv import load_dotenv

    load_dotenv()

    temp_path = Path.cwd()
    temp_path = Path(temp_path.joinpath(os.getenv("TEMP_REPORT_DIR")))
    dockers_run = int(os.getenv("AMOUNT_DOKER_RUN"))

    # Регистриуем роутеры в диспетчере
    fill.include_routers_in_dispatcher(dispatcher)

    # Пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем polling и систему проверки тестов в конкурентном режиме
    await asyncio.gather(
        dispatcher.start_polling(bot),
        AnswerProcessing(bot).run(),
        TaskProcessing(temp_path, dockers_run).run()
    )

if __name__ == '__main__':
    init_app()
    asyncio.run(main())