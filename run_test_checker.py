"""
Модуль запуска подсистемы проверки ответов в отдельном процессе
Example:
    $ python run_test_checker.py
"""
import asyncio
from pathlib import Path

from testing_tools.checker.task_processing import TaskProcessing
from utils.init_app import init_app
from config import settings


async def main():
    await init_app()
    temp_path = Path.cwd()
    temp_path = Path(temp_path.joinpath(settings.TEMP_REPORT_DIR))
    dockers_run = int(settings.AMOUNT_DOKER_RUN)
    await TaskProcessing(temp_path, dockers_run).run()

if __name__ == "__main__":
    asyncio.run(main())
