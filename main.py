# main.py
import asyncio
from aiogram import Dispatcher

from utils.init_app import init_app
from homeworkbot import bot, dispatcher
from homeworkbot import auth_handlers
from homeworkbot.admin_handlers import (
    admin_menu, add_chat,
    add_teacher, assign_teacher_to_group,
    add_student, add_discipline,
    add_students_group, ban_student,
    unban_student, assign_teacher_to_discipline,
    delete_group, delete_teacher, delete_student
)



async def main():
    # Регистриуем роутеры в диспетчере
    dispatcher.include_router(auth_handlers.router)
    dispatcher.include_router(admin_menu.router)
    dispatcher.include_router(add_chat.router)
    dispatcher.include_router(add_teacher.router)
    dispatcher.include_router(assign_teacher_to_group.router)
    dispatcher.include_router(add_student.router)
    dispatcher.include_router(add_discipline.router)
    dispatcher.include_router(add_students_group.router)
    dispatcher.include_router(ban_student.router)
    dispatcher.include_router(unban_student.router)
    dispatcher.include_router(assign_teacher_to_discipline.router)
    dispatcher.include_router(delete_student.router)
    dispatcher.include_router(delete_teacher.router)
    dispatcher.include_router(delete_group.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    init_app()
    asyncio.run(main())