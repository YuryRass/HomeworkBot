import json
from datetime import datetime

from database.main_db import common_crud
from model.pydantic.home_work import DisciplineHomeWorks
from model.pydantic.student_report import StudentReport


async def run_deadline_report_builder(
        student_id: int,
        discipline_id: int
) -> str:
    """Возвращает информацию по ближайшему дедлайну.

    Args:
        student_id (int): ID студента.
        discipline_id (int): ID дисциплины.

    Returns:
        str: информация о ближайшем дедлайне.
    """
    student_report = StudentReport()
    student = await common_crud.get_student_from_id(student_id)
    student_answer = await common_crud.get_student_discipline_answer(
        student_id,
        discipline_id
    )
    student_report.full_name = student.full_name
    home_works = DisciplineHomeWorks(
        **json.loads(student_answer.home_work)
    ).home_works

    current_date = datetime.now().date()

    deadline_failed = 0
    nearest_deadline = None
    for it in home_works:
        if current_date < it.deadline:
            nearest_deadline = it.deadline
            break
        elif it.end_time is not None:
            if it.deadline < it.end_time.date():
                deadline_failed += 1
        else:
            deadline_failed += 1

    if deadline_failed == len(home_works):
        return 'У меня для тебя плохие новости! Прожми батоны, т.к. ' \
               'завалены все дедлайны!!!'
    elif nearest_deadline is not None:
        return f'Ближайший дедлайн {nearest_deadline} в 23:59'
    else:
        return 'Сроки всех дедлайнов истекли! Если имеешь задолженность - ' \
               'напрягай батоны!!!'
