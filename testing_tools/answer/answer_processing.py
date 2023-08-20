"""Модуль реализует передачу ответов (по результатам тестов) студенту,
который отправил свою работу на проверку
"""
import asyncio
import json

from aiogram import Bot

from database.queue_db import queue_out_crud, rejected_crud
from model.pydantic.queue_out_raw import TestResult
from model.pydantic.test_rejected_files import TestRejectedFiles
from model.queue_db.queue_out import QueueOut


def _get_lab_number(name: str) -> int:
    """ункция ыозращает номер лаб. работы.

    Args:
        name (str): название лаб. работы.

    Returns:
        int: номер лаб. работы.
    """
    name = name.replace("-", "_")
    value = name.split("_")[-1]
    value = value.split('.')[0]
    return int(value)


class AnswerProcessing:
    """
    Класс опроса промежуточной БД и отправки результатов студенту
    """

    def __init__(self, bot: Bot,
                 amount_answer_process: int | None = None):
        """
        :param bot: ссылка на экземпляр бота
        :param amount_answer_process: количество обрабатываемых за раз записей.
        Если установлено в None - выгребаются все из таблицы БД
        """
        self.slice_size = amount_answer_process
        self.bot = bot

    async def run(self):
        while True:
            await asyncio.sleep(2)
            # проверяем сначала файлы, положительно прошедшие тесты
            if queue_out_crud.is_not_empty():
                records = queue_out_crud.get_all_records()
                if self.slice_size is not None:
                    if self.slice_size < len(records):
                        records = records[:self.slice_size]
                await self.__processing_records(records)

            # теперь файлы, не прошедшие систему тестирования
            while rejected_crud.is_not_empty():
                record = rejected_crud.get_first_record()
                await asyncio.sleep(1)
                rejected = TestRejectedFiles(**json.loads(record.data))

                # записываем причину отклонения файла
                text = f'<i>{rejected.description}:</i>'

                # добавляем все названия файлов
                for it in rejected.files:
                    text += f' \n<b>{it}</b>'
                await self.bot.send_message(
                    chat_id=record.chat_id,
                    text=text,
                )

    async def __processing_records(self, records: list[QueueOut]) -> None:
        """
        Метод подготовки и отправки ответа по результатам
        проверки заданий работы

        :param records: записи результатов

        :return: None
        """
        for record in records:
            test_result = TestResult(**json.loads(record.data))

            # результаты тестов в отсортированном порядке
            text = '<i>Результат тестирования:</i>\n'
            test_result.successful_task.sort(
                key=lambda x: _get_lab_number(x.file_name)
            )
            test_result.failed_task.sort(
                key=lambda x: _get_lab_number(x.file_name)
            )

            for it in test_result.successful_task:
                text += f'<b>✅ {it.file_name}</b>\n'
            for it in test_result.failed_task:
                text += f'<b>❌ {it.file_name}</b> {it.description}\n'
            await self.bot.send_message(
                chat_id=record.chat_id,
                text=text,
            )
            queue_out_crud.delete_record(record.id)
