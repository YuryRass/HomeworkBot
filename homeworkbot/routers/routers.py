"""Модуль создает роутеры, использующие при обработке апдейтов"""

from aiogram import Router

# роутер для команд админа, которые вводятся с клавиатуры
admin_router: Router = Router()

# роутер для команд админа и препода
common_router: Router = Router()

# роутеры для работы меню у админа, препода и студента
admin_menu_router: Router = Router()
teacher_menu_router: Router = Router()
student_menu_router: Router = Router()

# роутер для студента
student_router: Router = Router()