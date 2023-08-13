"""Модуль анализа callback-ов по созданию отчетов по учебным дисциплинам"""
import asyncio
import pathlib

from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile

from database.main_db import admin_crud, teacher_crud, common_crud
from homeworkbot import bot
from homeworkbot.routers import admin_router
from reports.run_report_builder import ReportBuilderTypeEnum, run_report_builder

# префиксы для callback-ов по созданию отчетов
__report_prefix = [
    'fullReport_',
    'fullGrReport_',
    'finishReport_',
    'finishGrReport_',
    'shortReport_',
    'shortGrReport_',
]

# словарь по переходу на следующий префикс
__next_step = {
    'fullReport': 'fullGrReport',
    'finishReport': 'finishGrReport',
    'shortReport': 'shortGrReport',
}


# типы отчетов
__reports_builder_type = {
    'fullGrReport': ReportBuilderTypeEnum.FULL,
    'finishGrReport': ReportBuilderTypeEnum.FINISH,
    'shortGrReport': ReportBuilderTypeEnum.SHORT,
}


def __is_download_prefix_callback(data: str) -> bool:
    """Функция проверки входа префикса в data.

    Args:
        data (str): строковые данные.

    Returns:
        bool: True, если префикс входит в data.
    """
    for it in __report_prefix:
        if it in data:
            return True
    return False


@admin_router.callback_query(lambda call: __is_download_prefix_callback(call.data))
async def callback_download_full_report(call: CallbackQuery):
    """Функуия обработки коллбэков по созданию отчетов успеваемости студентов.

    Args:
        call (CallbackQuery): коллбэк.
    """
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'fullReport' | 'finishReport' | 'shortReport':
            await call.message.edit_text(text="Выберете предмет")
            group_id = int(call.data.split('_')[1])

            # если tg пользователь - админ без прав на препода, то
            # получаем весь список дисциплин для выбранной группы.
            if admin_crud.is_admin_no_teacher_mode(call.from_user.id):
                disciplines = common_crud.get_group_disciplines(group_id)

            # в противном случае получаем те дисциплины, которые назначены преподу
            # для выбранной учебной группы.
            else:
                disciplines = teacher_crud.get_assign_group_discipline(
                    call.from_user.id,
                    group_id
                )
            # если список дисциплин пуст
            if len(disciplines) == 0:
                await call.message.edit_text(text="За группой не числится дисциплин")

            # если кол-во дисциплин > 1, то предоставляем право выбора одной из них
            elif len(disciplines) > 1:
                disciplines_kb = InlineKeyboardBuilder()
                disciplines_kb.row(
                    *[InlineKeyboardButton(
                        text=it.short_name,
                        callback_data=f'{__next_step[type_callback]}_{group_id}_{it.id}'
                    ) for it in disciplines]
                )
                await call.message.edit_text(
                    text="Выберите дисциплину:",
                    reply_markup=disciplines_kb.as_markup(),
                )
            # если len(disciplines) == 1, то создаем сразу отчет для нее
            else:
                await __create_report(
                    call,
                    group_id,
                    disciplines[0].id,
                    __reports_builder_type[__next_step[type_callback]]
                )

        # после того как пользователь выбрал дисциплину, делаем отчет
        case 'fullGrReport' | 'finishGrReport' | 'shortGrReport':
            group_id = int(call.data.split('_')[1])
            discipline_id = int(call.data.split('_')[2])
            await __create_report(call, group_id, discipline_id, __reports_builder_type[type_callback])

        case _:
            await call.message.edit_text(
                text="Неизвестный формат для обработки данных"
            )


async def __create_report(
        call: CallbackQuery,
        group_id: int,
        discipline_id: int,
        builder_type: ReportBuilderTypeEnum) -> None:
    """
    Функция запуска формирования отчета в отдельном потоке

    :param call: CallbackQuery для отправки отчета и редактирования сообщений в чате
    :param group_id: id группы по которой формируется отчет
    :param discipline_id: id дисциплины по которой формируется отчет
    :param builder_type: тип формируемого отчета

    :return: None
    """
    await call.message.edit_text(text="Начинаем формировать отчет")

    # формируем отчет об успеваемости студентов в отдельном потоке
    # в неблокирующем режиме.
    path_to_report = await asyncio.gather(
        asyncio.to_thread(run_report_builder, group_id, discipline_id, builder_type)
    )

    await call.message.edit_text(text="Отчет успешно сформирован")

    await bot.send_document(
        call.message.chat.id,
        FSInputFile(pathlib.Path(path_to_report[0]))
    )