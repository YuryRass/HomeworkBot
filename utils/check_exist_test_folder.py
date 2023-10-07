"""Модуль, проверяющий что папка с тестами существует"""

import os
from pathlib import Path

from database.main_db import common_crud


async def is_test_folder_exist(discipline_id: int, work_id: int) -> bool:
    """Функция проверки существования папки с тестами
    по лаб. работе для выбранной учебной дисциплины

    Args:
        discipline_id (int): ID дисциплины.
        work_id (int): ID лаб. работы.

    Returns:
        bool: True, если директория с тестами существует.
    """
    discipline = await common_crud.get_discipline(discipline_id)
    return os.path.exists(
        Path.cwd().joinpath(
            discipline.path_to_test
        ).joinpath(str(work_id))
    )
