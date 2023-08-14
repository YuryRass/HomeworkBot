"""Модуль создает роутеры, использующие при обработке апдейтов"""

from aiogram import Router

admin_router: Router = Router()

common_router: Router = Router()


admin_menu_router: Router = Router()
admin_router: Router = Router()

teacher_menu_router: Router = Router()

student_router: Router = Router()