"""
    Модуль disciplines_utils.py предназначен
    для работы с учебными дисциплинами
"""
import json

from model.pydantic.discipline_works import DisciplinesConfig, \
    DisciplineWorksConfig


def load_disciplines_config(file_path: str) -> DisciplinesConfig:
    """Конвертирует данные по учебным дисциплинам из JSON файла
       в pydantic модель и возвращает ее.
       Параметры:
       file_path (str): путь до JSON файла.
    """
    with open(file_path, encoding='utf-8') as json_file:
        data = json.load(json_file)
        return DisciplinesConfig(**data)


def disciplines_config_to_json(data: DisciplinesConfig) -> str:
    """
        Конвертирует pydantic модель 'Конфигурация дисциплин'
        в JSON формат в виде строки и возвращает ее.
        Параметры:
        data (DisciplinesConfig): конфиг. данные учебных дисциплин.

    """
    return data.model_dump_json(indent=4, exclude_none=True)


def disciplines_config_from_json(json_data: str) -> DisciplinesConfig:
    """
        Возвращает pydantic модель 'Конфигурация дисциплин' из JSON файла.
        Параметры:
        json_data (str): конфиг. данные по учебным дисциплинам в JSON формате.
    """
    data = json.loads(json_data)
    return DisciplinesConfig(**data)


def disciplines_works_to_json(data: DisciplineWorksConfig) -> str:
    """
        Конвертирование pydantic модели 'Конфигурация работ дисциплины'
        в JSON формат.
        Параметры:
        data (DisciplineWorksConfig): конфиг. данные работ по дисциплине.
    """
    return data.model_dump_json(indent=4, exclude_none=True)


def disciplines_works_from_json(
    json_data: str | bytes
) -> DisciplineWorksConfig:
    """
        Загрузка учебной дисциплины и перевод ее данных в pydantic модель
        Параметры:
        json_data (str): массив данных по учебной дисциплине.
    """
    data = json.loads(json_data)
    return DisciplineWorksConfig(**data)


def counting_tasks(discipline: DisciplineWorksConfig) -> int:
    """
        Возвращает количество домашних заданий по учебной дисциплине
        Параметры:
        discipline (DisciplineWorksConfig): конфиг. данные работ по дисциплине.
    """
    result = 0
    # в рамках некоторой учебной дисциплины пробегаем по всем лаб. работам
    # и подсчитываем общее количество домашних заданий.
    for it in discipline.works:
        result += it.amount_tasks
    return result
