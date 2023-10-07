"""Модуль формирует соответсвующий отчет успеваемости студентов по учебной дисциплине.
"""
from enum import Enum

from reports.base_report_builder import BaseReportBuilder
from reports.finish_report_builder import FinishReportBuilder
from reports.full_report_builder import FullReportBuilder
from reports.short_report_builder import ShortReportBuilder


class ReportBuilderTypeEnum(Enum):
    FINISH = 1
    FULL = 2
    SHORT = 3


async def run_report_builder(
        group_id: int,
        discipline_id: int,
        builder_type: ReportBuilderTypeEnum) -> str:
    """
    Функция запуска формирования файлового отчета

    :param group_id: id группы по которой формируется отчет
    :param discipline_id: id дисциплины по которой формируется отчет
    :param builder_type: тип формируемого отчета

    :return: путь до сформированного отчета
    """
    report_builder: BaseReportBuilder | None = None
    match builder_type:
        case ReportBuilderTypeEnum.FINISH:
            report_builder = await FinishReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.FULL:
            report_builder = await FullReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.SHORT:
            report_builder = await ShortReportBuilder(group_id, discipline_id)
    await report_builder.build_report()
    report_builder.save_report()
    path: str = report_builder.get_path_to_report()
    return path
