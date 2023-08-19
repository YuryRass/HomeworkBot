import shutil
from datetime import datetime
from pathlib import Path

from config import settings

def create_answers_archive(path_to_group_folder: Path) -> Path:
    """
    Функция формирования архива ответов группы.

    :param path_to_group_folder: путь до директории группы, где хранятся ответы.

    :return: путь до сформированного архива.
    """
    # путь до папки, где будет храниться архив с ответами
    path = Path(Path.cwd().joinpath(settings.TEMP_REPORT_DIR))

    # название архива
    file_name = f'data_{datetime.now().date()}'

    # архивируем ответы студентов, находящиеся в папке path_to_group_folder,
    # потом помещаем архив в папку path и даем ему название file_name
    # с расширением .zip
    shutil.make_archive(
        str(path.joinpath(f'{file_name}')),
        'zip', path_to_group_folder
    )

    return path.joinpath(f'{file_name}.zip')