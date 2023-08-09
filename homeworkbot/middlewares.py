from typing import Callable, Dict, Any, Awaitable

from aiogram import Bot, BaseMiddleware
from aiogram.types import TelegramObject

from database.main_db import common_crud


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
        if not common_crud.is_ban(event.from_user.id):
            return await handler(event, data)

        # если студент - в бан-листе.
        await event.answer(
                f'Функциональность бота недоступна, вы в бан-листе!!! '
                f'Для разблокировки обратитесь к своему преподавателю!'
            )
        return
