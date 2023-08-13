"""Модуль реализует построение полного отчета на основе базового отчета"""
import json

from database.main_db import common_crud
from model.pydantic.home_work import DisciplineHomeWorks
from reports.base_report_builder import BaseReportBuilder, ReportFieldEnum


class FullReportBuilder(BaseReportBuilder):

    def __init__(self, group_id: int, discipline_id: int):
        # создаем excel-файл с полным отчетом, где пока еще
        # содержатся данные базового отчета.
        super().__init__(group_id, discipline_id, 'full_report')

    def build_report(self) -> None:
        # сначала создаем базовый отчет и к нему уже добавляем оставшиеся данные
        # для полноты сведений о выполнении лаб. работ студентами.
        super().build_report()

        # получаем excel страницу, куда будем дозаписывать данные
        worksheet = self.wb.active

        students = common_crud.get_students_from_group(self.group_id)
        row = 1
        for student in students:
            # результаты по выполнению лаб. работ студентами
            answers = common_crud.get_student_discipline_answer(student.id, self.discipline_id)
            home_works = DisciplineHomeWorks(**json.loads(answers.home_work)).home_works

            if row == 1:
                # дополняем заголовок справа номерами заданий для каждой лаб. работы
                col = ReportFieldEnum.NEXT
                for number_lab, work in enumerate(home_works):
                    for number_task, task in enumerate(work.tasks):
                        worksheet.cell(
                            row=row, column=col
                        ).value = f'lab{number_lab+1}_Q{number_task+1}'
                        col += 1

                row += 1

            # теперь пошли и сами данные
            if row > 1:
                col = ReportFieldEnum.NEXT
                # если задание лаб. работы у студента выполнено, то присваиваем
                # ей значение 1 и окрашиваем в зеленый цвет. В противном случае -
                # в красный цввет и окрашиваем в красный цвет.
                for number_lab, work in enumerate(home_works):
                    for number_task, task in enumerate(work.tasks):
                        worksheet.cell(
                            row=row, column=col
                        ).value = 1 if task.is_done else 0

                        if task.is_done:
                            worksheet.cell(
                                row=row,
                                column=col
                            ).fill = BaseReportBuilder.GREEN_FILL
                        else:
                            worksheet.cell(
                                row=row,
                                column=col
                            ).fill = BaseReportBuilder.RED_FILL

                        col += 1
            row += 1