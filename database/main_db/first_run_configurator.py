"""
    Модуль для получения первоначальной информации
    по инициализации БД и создания учебных директорий.
"""
from pathlib import Path

from utils.disciplines_utils import *
from utils.homework_utils import *
from utils.excel_parser import ExcelDataParser, StudentRaw, TeacherRaw


class FirstRunConfigurator:
    """
        Класс, содержащий конфиг. данные
        для первоначальной инициализации основной БД
    """
    def __init__(self, disciplines_path: str, excel_path: str):
        """
            Параметры:
            disciplines_path (str): путь до JSON файла с дисциплинами.
            excel_path (str): путь до excel файла с данными
        о студентах и преподах.
        """
        # данные о студентах и преподах
        excel_init_data = ExcelDataParser(excel_path)

        self.__disciplines = load_disciplines_config(disciplines_path)
        self.__students = excel_init_data.students
        self.__teachers = excel_init_data.teachers
        self.__create_directory()

    def __create_directory(self):
        """
            Создание директорий, которые будут содержать
            тесты для студенческих программ и ответы студентов,
            по различным учебным дисциплинам.
        """
        path = Path.cwd() # current work directory
        for it in self.__disciplines.disciplines:
            Path(path.joinpath(it.path_to_test)).mkdir(parents=True, exist_ok=True)
            Path(path.joinpath(it.path_to_answer)).mkdir(parents=True, exist_ok=True)

    def counting_tasks(self, discipline: DisciplineWorksConfig) -> int:
        """Возвращает количество домашних заданий по дисциплине."""
        return counting_tasks(discipline)

    @property
    def disciplines(self) -> list[DisciplineWorksConfig]:
        """Возвращает список учебных дисциплин."""
        return self.__disciplines.disciplines

    @property
    def students_config(self) -> dict[str, dict[str, list[StudentRaw]]]:
        """Возвращает словарь с данными о студентах"""
        return self.__students

    @property
    def teachers_config(self) -> dict[str, dict[str, list[TeacherRaw]]]:
        """Возвращает словарь с данными о преподах"""
        return self.__teachers

    def create_empty_homework_json(self, discipline_short_name: str) -> str:
        """
            Возвращает данные по лабораторным работам
            для учебной дисциплины в JSON формате.
            Параметры:
            discipline_short_name (str): короткое название учебной дисциплины.
        """
        #
        discipline: DisciplineWorksConfig = None
        for it in self.disciplines:
            if it.short_name == discipline_short_name:
                discipline = it

        if discipline is None:
            raise Exception(f'Discipline with short name "{discipline_short_name}" not found')

        empty_homework: DisciplineHomeWorks = create_homeworks(discipline)
        return homeworks_to_json(empty_homework)

    def disciplines_works_to_json(self, discipline: DisciplineWorksConfig) -> str:
        """
            Возвращает конфигурацию лаб. работ учебной дисциплины в JSON формате.
        Применяется в таблице 'disciplines' в столбце 'works'.
            Параметры:
            discipline (DisciplineWorksConfig): конфигурация лаб. работ учебной дисциплины
        """
        return disciplines_works_to_json(discipline)