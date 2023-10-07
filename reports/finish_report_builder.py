"""Построение окончательного отчета на основе базового отчета.
"""
from asyncinit import asyncinit
from reports.base_report_builder import BaseReportBuilder


@asyncinit
class FinishReportBuilder(BaseReportBuilder):
    async def __init__(self, group_id: int, discipline_id: int):
        await super().__init__(group_id, discipline_id, 'finish_report')
