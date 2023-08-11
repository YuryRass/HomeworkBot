__all__ = [
    'add_chat', 'add_teacher', 'assign_teacher_to_group',
    'add_student', 'add_discipline', 'add_students_group',
    'ban_student', 'unban_student', 'assign_teacher_to_discipline',
    'delete_group', 'delete_teacher', 'delete_student'
]


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
import homeworkbot.admin_handlers.delete_group as delete_group
import homeworkbot.admin_handlers.delete_teacher as delete_teacher
import homeworkbot.admin_handlers.delete_student as delete_student

from homeworkbot.admin_handlers.admin_menu import first_admin_keyboard as admin_keyboard