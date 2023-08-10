__all__ = ['admin_menu', 'admin_keyboard']


import homeworkbot.admin_handlers.admin_menu as admin_menu
import homeworkbot.admin_handlers.add_chat as add_chat
import homeworkbot.admin_handlers.add_teacher as add_teacher
import homeworkbot.admin_handlers.assign_teacher_to_group as assign_teacher_to_group
import homeworkbot.admin_handlers.add_student as add_student
import homeworkbot.admin_handlers.add_discipline as add_discipline
import homeworkbot.admin_handlers.add_students_group as add_students_group
import homeworkbot.admin_handlers.ban_student as ban_student
import homeworkbot.admin_handlers.unban_student as unban_student
import homeworkbot.admin_handlers.assign_teacher_to_discipline as assign_teacher_to_discipline

from homeworkbot.admin_handlers.admin_menu import first_admin_keyboard as admin_keyboard