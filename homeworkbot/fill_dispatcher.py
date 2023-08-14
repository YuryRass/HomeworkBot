"""Модуль включает все роутеры в рамках Tg бота в диспетчер"""

from aiogram import Dispatcher

from homeworkbot.auth_handlers import auth_router

# инициализиация роутеров админа и препода
from homeworkbot.admin_handlers import *
from homeworkbot.teacher_handlers import *
from homeworkbot.student_handlers import *

from homeworkbot.routers import (
    admin_menu_router, admin_router,
    teacher_menu_router, common_router,
    student_menu_router, student_router
)

def include_routers_in_dispatcher(dispatcher: Dispatcher) -> None:
    """Функция регистриурет роутеры в диспетчере.

    Args:
        dispatcher (Dispatcher): сам диспетчер.
    """
    # Регистриуем роутер для аутентификации Tg пользователя
    dispatcher.include_router(auth_router)

    # Регистрируем роутеры админа, препода и студента в диспетчере
    dispatcher.include_router(admin_menu_router)
    dispatcher.include_router(teacher_menu_router)
    dispatcher.include_router(student_menu_router)

    dispatcher.include_router(admin_router)
    dispatcher.include_router(common_router)