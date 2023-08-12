import os
from shutil import rmtree
from pathlib import Path
from zipfile import ZipFile


class DeleteFileException(Exception):
    ...


async def save_test_files(path_to_test: str, downloaded_file: bytes) -> None:
    """
        Функция распаковки архива тестов по дисциплине.

        :param downloaded_file: сырое представление архива (набор байт).
        :param path_to_test: корневая директория загрузки тестов по
        выбранной студентом дисциплине.

        :return: None
        """
    path = Path.cwd()
    path = Path(path.joinpath(path_to_test)) # полный путь до тестов

    # удаляем, если они имеютя, все файлы в папке path
    if os.listdir(path):
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    rmtree(file_path)
            except Exception as ex:
                raise DeleteFileException(f'<b>Failed to delete</b> <i>{file_name}</i>. Reason: {ex}')

    # записываем загруженные данные в архив
    with open(path.joinpath('archive.zip'), "wb") as new_file:
        new_file.write(downloaded_file)

    # извлекаем все данные из архива в папку path
    with ZipFile(path.joinpath('archive.zip')) as zipObj:
        zipObj.extractall(path=Path(path))