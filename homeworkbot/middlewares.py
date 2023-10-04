"""Модуль реализует промежуточные ПО"""

from datetime import timedelta
from enum import Enum, auto
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.main_db import student_crud, common_crud


class BanMiddleware(BaseMiddleware):
    """
    Класс промежуточного ПО, внедряемого в бота для отсечения забаненных
    студентов от функциональности системы.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Если студент не находится в бан-листе,
        # то продолжаем обработку апдейта.
        if not await common_crud.is_ban(event.from_user.id):
            return await handler(event, data)

        # если студент - в бан-листе.
        await event.answer(
                text='Функциональность бота недоступна, вы в бан-листе!!!\n' +
                'Для разблокировки обратитесь к своему преподавателю!'
            )
        return


class FloodMiddlewareState(Enum):
    """Класс состояний по загрузке ответов студентами"""

    # загрузка ответов уже произведена
    # (повторная загрузка может быть через определенный интервал времени)
    UPLOAD_ANSWER = auto()
    # одидание загрузки ответов студентом
    WAIT_UPLOAD_ANSWER = auto()


class StudentFloodMiddleware(BaseMiddleware):
    """
    Класс промежуточного ПО, внедряемого в бота для лимитирования запросов
    студентов на загрузку ответов на л/р (д/р) и команд на проверку
    успеваимости
    """
    def __init__(self, load_answers_limit: int, commands_limit: int) -> None:
        """
        :param load_answers_limit: ограничение (в минутах) на период загрузки
        ответов
        :param commands_limit: ограничение (в минутах) на период запросов
        данных об успеваимости

        :return:
        """

        self.last_answer_time = {}  # время последней зарузки ответов студентом

        # время последнего запроса данных об успеваимости студента
        self.last_command_time = {}

        # словарь состояний со значениями класса FloodMiddlewareState
        self.state = {}

        # период времени (в секундах), через который можно
        # повторно загрузить ответы студенту
        self.load_answers_limit = timedelta(seconds=load_answers_limit*60)

        # период времени (в секундах), через который
        # студенту можно узнать про свою успеваемость
        self.commands_limit = timedelta(seconds=commands_limit*60)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if student_crud.is_student(event.from_user.id):
            if event.text in [
                'Ближайший дедлайн', 'Успеваимость', 'Загрузить ответ'
            ]:
                if (not event.from_user.id in self.last_answer_time and
                        event.text == 'Загрузить ответ'):
                    self.state[event.from_user.id] = \
                        FloodMiddlewareState.WAIT_UPLOAD_ANSWER
                    self.last_answer_time[event.from_user.id] = event.date
                    return await handler(event, data)

                if (not event.from_user.id in self.last_command_time and
                        event.text in ['Ближайший дедлайн', 'Успеваимость']):
                    self.last_command_time[event.from_user.id] = event.date
                    return await handler(event, data)

                is_not_success = False  # флаг доступа студента

                # время, через котрое можно будет обратиться к боту студенту
                last_time = 0

                match event.text:
                    case 'Загрузить ответ':
                        if (event.date - self.last_answer_time[event.from_user.id] <
                                self.load_answers_limit):
                            last_time = self.load_answers_limit
                            last_time -= event.date - self.last_answer_time[event.from_user.id]
                            is_not_success = True
                        else:
                            self.state[event.from_user.id] = \
                                FloodMiddlewareState.WAIT_UPLOAD_ANSWER
                            self.last_answer_time[event.from_user.id] = event.date
                            return await handler(event, data)
                    case _:
                        if (event.date - self.last_command_time[event.from_user.id] <
                                self.commands_limit):
                            last_time = self.commands_limit
                            last_time -= event.date - self.last_command_time[event.from_user.id]
                            is_not_success = True
                        else:
                            self.last_command_time[event.from_user.id] = event.date
                            return await handler(event, data)

                if is_not_success:
                    minutes = (last_time.seconds % 3600) // 60
                    minutes = f' {minutes} мин.' if minutes > 0 else ''
                    seconds = last_time.seconds % 60
                    await event.answer(
                        text=f'Лимит до следующего обращения к боту еще не истек!!!'
                        f'Обратитесь к боту через{minutes} {seconds} с.'
                    )
                    return

            elif event.text == '/start':
                return await handler(event, data)
            else:
                if (
                    self.state and
                    self.state[event.from_user.id] == FloodMiddlewareState.WAIT_UPLOAD_ANSWER and
                    event.content_type == 'document'
                ):
                    self.state[event.from_user.id] = FloodMiddlewareState.UPLOAD_ANSWER

                return await handler(event, data)
        # для других Tg-пользователей:
        else:
            return await handler(event, data)