import json

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database.main_db.crud_exceptions import DisciplineNotFoundException, GroupAlreadyExistException
from homeworkbot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message
from homeworkbot.filters import IsNotOnlyAdmin, IsOnlyAdmin
from homeworkbot.configuration import bot
from database.main_db import admin_crud
from model.pydantic.students_group import StudentsGroup

router: Router = Router()


class AdminStates(StatesGroup):
    upload_students_group = State()


@router.message(IsOnlyAdmin(), Command(commands=['addstudentsgroup']))
async def handle_add_students_group(message: Message):
    await _handle_add_students_group(message)


@router.message(IsNotOnlyAdmin(), Command(commands=['addstudentsgroup']))
async def handle_no_add_students_group(message: Message):
    await message.answer(text="Нет прав доступа!!!")


async def _handle_add_students_group(message: Message, state: FSMContext):
    await state.set_state(state=AdminStates.upload_students_group)
    await message.answer(
        "Загрузите json-файл с конфигурацией новой группы и "
        "назначенной ей дисциплины, которая уже существует в системе:"
    )


@router.message(StateFilter(AdminStates.upload_students_group),
                     F.content_type == ContentType.DOCUMENT)
async def handle_upload_students_group(message: Message, state: FSMContext):
    """
        Обработчик загрузки группы студентов
        и добавления их в БД.
    """
    # сообщение о начале загрузки файла
    result_message = await start_upload_file_message(message)

    file_type = message.document.mime_type
    if file_type == 'application/json':
        file_info = await bot.get_file(message.document.file_id)

        # получаем экземпляр байтового потока с данными из файла
        downloaded_file = await bot.download_file(file_info.file_path)

        # загружаем данные по группам студентов в JSON формате
        group_data = json.loads(downloaded_file.read())

        # создаем список групп студентов
        groups_list = [StudentsGroup(**it) for it in group_data]

        try:
            # добавляем группы студентов в БД
            admin_crud.add_students_group(groups_list)

            # оповещаем о завершении загрузки файла
            await finish_upload_file_message(
                result_message,
                f'<i>Группа(ы) студентов успешно дабавлена(ы)!</i>'
            )
            # очистка состояния админа
            await state.clear()

        except DisciplineNotFoundException as dnf_ex:
            await result_message.edit_text(text=str(dnf_ex))

        except GroupAlreadyExistException as gae_ex:
            await result_message.edit_text(text=str(gae_ex))
    else:
        await result_message.edit_text(text="Неверный тип файла")