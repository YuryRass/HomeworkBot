"""
    Модуль add_student.py позволяет на правах админа
    добавить нового студента в БД и назначить ему дисицплину.
"""
import re
from enum import IntEnum

from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from pydantic import BaseModel
from aiogram.types import (
    InlineKeyboardButton, Message, CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main_db import admin_crud, common_crud
from homeworkbot.filters import AddStudentCallbackFactory, IsOnlyAdmin, IsNotOnlyAdmin
from homeworkbot.routers import admin_router


class AddStudentStep(IntEnum):
    SAVE = 1 # добавление студента в БД
    DISCIPLINE = 2 # выбор дисциплины для студента


class ProcessAddStudent(BaseModel):
    """
        Процесс добавления студента.
        Предназначен для инициализации callback-ов.
        Сам full_name студента не используем, поскольку
        с ним длина callback-а может превысить 64 байта.
    """
    discipline_id: int = 0
    group_id: int = 0
    next_step: int = 0


class AdminStates(StatesGroup):
    """
        Состояния админа.
        Сюда записывается full_name студента.
    """
    student_name = State()


@admin_router.message(IsOnlyAdmin(), Command(commands=['addstudent']))
async def handle_add_student(message: Message):
    """
        Обработчик установки состояния админа на добавления студента.
    """
    await _handle_add_student(message)


@admin_router.message(IsNotOnlyAdmin(), Command(commands=['addstudent']))
async def handle_no_add_student(message: Message):
    """
        Обработчик невозможности установки состояния
        админа на добавления студента.
    """
    await message.answer(text="Нет прав доступа!!!")


async def _handle_add_student(message: Message, state: FSMContext):
    """
        Функция установки состояния админа на добавление студента.
        Параметры:
        message (Message): сообщение Tg-пользователя.
    """
    await state.set_state(state=AdminStates.student_name)
    await message.answer(text="Введите ФИО студента:")


@admin_router.message(StateFilter(AdminStates.student_name))
async def student_name_correct(message: Message, state: FSMContext):
    """
        Обработчик проверки ФИО студента и вывода списка учебных групп.
    """
    fio_pattern: re.Pattern = re.compile(
        r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]')

    if fio_pattern.match(message.text):
        # получаем список всех групп
        groups = admin_crud.get_all_groups()

        if len(groups) < 1:
            await message.answer(text="В БД отсутствуют группы, куда можно добавить студента!")
            return
        # список с инлаин-кнопками, на которых написаны названия групп
        # и содержатся данные о студенте
        group_inline_button = []

        # заполнение списка group_inline_button
        for it in groups:
            group_inline_button.append(
                InlineKeyboardButton(
                    text=it.group_name,
                    callback_data=AddStudentCallbackFactory(
                        group_id=it.id,
                        discipline_id=-1, # значение на первоначальном этапе
                        next_step=int(AddStudentStep.DISCIPLINE)
                    ).pack()
                )
            )
        # предоставляем пользователю возможность назначения группы для студента
        groups_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
        groups_kb.row(*group_inline_button, width=1)
        await message.answer(
            text="Выберите группу студента:",
            reply_markup=groups_kb.as_markup(),
        )
        # добавляем данные и убираем состояние
        await state.update_data(student_name=message.text)
        await state.set_state(state=None)
    # Некорректный ввод ФИО:
    else:
        await message.answer(text="Пожалуйста, проверьте корректность ввода ФИО!")


@admin_router.callback_query(AddStudentCallbackFactory.filter())
async def callback_add_student(call: CallbackQuery, state: FSMContext):
    """
        Обработчик добавления студента и назначения ему дисциплин.
    """
    # получение данных о студенте из callback-а
    _, group_id, discipline_id, next_step = call.data.split('_')
    student_data: ProcessAddStudent = ProcessAddStudent(
        discipline_id=discipline_id,
        group_id=group_id,
        next_step=next_step
    )

    # Исследование next_step
    match student_data.next_step:
        case AddStudentStep.DISCIPLINE: # назначение дисципины для студента

            # получаем список дисциплин для учебной группы
            disciplines = common_crud.get_group_disciplines(student_data.group_id)
            if len(disciplines) < 1:
                await call.message.edit_text(text="В БД отсутствуют данные по дисциплинам!")
                return
            # cоздаем инлаин-кнопки с дисциплинами для учебной группы
            discipline_inline_button = []
            for it in disciplines:
                discipline_inline_button.append(
                    InlineKeyboardButton(
                        text=it.short_name,
                        callback_data=AddStudentCallbackFactory(
                            group_id=student_data.group_id,
                            discipline_id=it.id,
                            next_step=int(AddStudentStep.SAVE),
                        ).pack()
                    )
                )
            disc_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
            disc_kb.row(*discipline_inline_button, width=1)

            # предоставляем возможность выбора дисицплины для студента
            await call.message.edit_text(
                text="Выберите дисциплину по которой обучается студент:",
                reply_markup=disc_kb.as_markup()
            )
        # добавляем студента
        case AddStudentStep.SAVE:
            student_name = await state.get_data()
            admin_crud.add_student(
                student_name['student_name'],
                student_data.group_id,
                student_data.discipline_id
            )
            await state.set_data({}) # убираем данные о ФИО
            await call.message.edit_text(text="Студент успешно добавлен!")
        case _:
            await call.message.edit_text(text="Неизвестный формат для обработки данных")