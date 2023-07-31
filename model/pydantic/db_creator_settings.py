"""
    Модуль db_creator_settings.py реализует класс для хранения
    конфиг. информации по первоначальной инициализации основной БД
"""
from dataclasses import dataclass


@dataclass
class DbCreatorSettings:
    """
        Класс, содержащий конфигурационную информацию
    для первоначальной инициализации основной БД
        Атрибуты:
        remote_configuration (bool): флаг для удаленной инициализации БД
    (Если remote_configuration is True, то БД заполняется из данных,
    находящихся в файлах disciplines_path и excel_data_path).
        default_admin (int): Telegram ID администратора.
        disciplines_path (str): путь до JSON файла, где содержится
    информация по учебным дисциплинам.
        excel_data_path (str): путь до Excel файла, где содержится
    информация по студентам и преподавателям.

    """
    remote_configuration: bool
    default_admin: int | None = None
    disciplines_path: str = ''
    excel_data_path: str = ''
