from aiogram import F
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, Message,
    ContentType
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter

from database.main_db import common_crud
from database.queue_db import queue_in_crud
from model.pydantic.queue_in_raw import QueueInRaw
from utils.check_exist_test_folder import is_test_folder_exist
from utils.unzip_homework_files import save_homework_file

from homeworkbot.configuration import bot
from homeworkbot.routers import student_router


class StudentStates(StatesGroup):
    upload_answer = State()


@student_router.callback_query(
    lambda call: "uploadAnswer_" in call.data or "labNumber" in call.data
)
async def handle_upload_answer(call: CallbackQuery, state: FSMContext):
    """Обработчик по началу загрузки ответов студентом.

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "uploadAnswer":
            discipline_id = int(call.data.split("_")[1])
            discipline = await common_crud.get_discipline(discipline_id)
            labs_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
            labs_kb.row(
                *[
                    InlineKeyboardButton(
                        text=f"Лаб. раб. № {it}",
                        callback_data=f"labNumber_{it}_{discipline_id}",
                    )
                    for it in range(1, discipline.max_home_works + 1)
                ],
                width=1
            )
            await call.message.edit_text(
                text="Выберете номер лабораторной работы",
                reply_markup=labs_kb.as_markup()
            )
        case "labNumber":
            number = int(call.data.split("_")[1])
            if not await is_test_folder_exist(
                int(call.data.split("_")[2]), number
            ):
                await call.message.edit_text(
                    text="К сожалению, тесты для этой работы еще не готовы!",
                )
                return
            await call.message.edit_text(
                text="Загрузите ответы в zip файле",
            )
            await state.set_state(state=StudentStates.upload_answer)

            # добавление значений
            await state.update_data(labNumber=number)
            await state.update_data(discipline_id=int(call.data.split("_")[2]))
        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных"
            )


@student_router.message(
    StateFilter(StudentStates.upload_answer),
    F.content_type == ContentType.DOCUMENT
)
async def handle_student_docs(message: Message, state: FSMContext):
    """Обработчик по загрузке ответов студентов.

    Args:
        message (Message): Tg сообщение.
    """
    result_message = await message.answer(
        text="<i>Загружаем ваш файл...</i>",
        disable_web_page_preview=True,
    )

    # получение данных
    data = await state.get_data()
    lab_num = data["labNumber"]
    discipline_id = data["discipline_id"]

    discipline = await common_crud.get_discipline(discipline_id)

    file_name = message.document.file_name
    if file_name[-4:] == ".zip":
        if message.document.file_size > 10000:
            await result_message.answer(
                text="<i>Архив превысил разрешенный к загрузке размер!!!</i>",
            )
            await state.clear()
            return

        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        filelist = await save_homework_file(
            file_name,
            downloaded_file.read(),
            message.from_user.id,
            lab_num,
            discipline.path_to_answer,
        )

        await queue_in_crud.add_record(
            message.from_user.id,
            message.chat.id,
            QueueInRaw(
                discipline_id=discipline_id,
                files_path=filelist,
                lab_number=lab_num
            )
        )

        await message.answer(text="Задания отправлены на проверку")

    else:
        await message.answer(text="Неверный тип файла")
    await result_message.edit_text(
        text="<i>Файл загружен!</i>",
    )
    await state.clear()
