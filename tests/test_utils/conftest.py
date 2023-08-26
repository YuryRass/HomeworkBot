import os
from datetime import date
from shutil import rmtree
from zipfile import ZipFile
from pathlib import Path
import pytest

from model.pydantic.discipline_works import (
    DisciplineWork, DisciplineWorksConfig,
    DisciplinesConfig
)

from model.pydantic.home_work import (
    DisciplineHomeWorks, HomeWork, HomeTask
)

from model.pydantic.db_start_data import StudentRaw, TeacherRaw

from _json_data_for_tests import (
    error_disciplines_json, disciplines_json,
    discipline_works_json, error_discipline_works_json
)

from _json_data_for_tests import (
    discipline_home_works_json, error_discipline_home_works_json
)

from utils.excel_parser import ExcelDataParser, ParserType


class UnzipTestFiles:
    @pytest.fixture
    def out_dir(self):
        # директория, куда будут помещаться распакованные файлы
        out_dir = 'out'
        out_dir = Path.cwd().joinpath('tests').joinpath(out_dir)
        Path.mkdir(out_dir, parents=True, exist_ok=True)

        # заполняем out_dir временными файлами для тестов
        Path.mkdir(out_dir.joinpath('temp_dir'), parents=True, exist_ok=True)
        open(out_dir.joinpath('temp_file'), 'w')
        return out_dir

    @pytest.fixture
    def zip_file(self):
        # создаем архив in.zip с пятью пустыми файлами
        zip_file = 'in.zip'
        zip_file = Path.cwd().joinpath('tests').joinpath(zip_file)

        with ZipFile(zip_file, 'w') as my_zip:
            for i in range(5):
                fname = Path.cwd().joinpath('tests').joinpath(f'file_{i}.py')
                open(fname, 'w')
                my_zip.write(
                    fname, os.path.relpath(
                        fname, Path.cwd().joinpath('tests')
                    )
                )

        return zip_file

    @pytest.fixture
    def downloaded_file(self, zip_file):
        # сырое представление архива in.zip
        with open(zip_file, 'rb') as myzip:
            downloaded_file = myzip.read()
        return downloaded_file

    @pytest.fixture
    def delete_all_files(self, out_dir, zip_file):
        yield
        # удаляем все созданные раннее файлы
        for i in range(5):
            fname = Path.cwd().joinpath('tests').joinpath(f'file_{i}.py')
            if os.path.isfile(fname):
                os.remove(fname)
        if os.path.isfile(zip_file):
            os.remove(zip_file)
        if os.path.isdir(out_dir):
            rmtree(out_dir)


class DisciplinesUtils:
    @pytest.fixture
    def disciplines_config(self) -> str:
        discipline_work: list[DisciplineWork] = [
            DisciplineWork(
                number=i+1,
                amount_tasks=2,
                deadline=date(2020, 11, 28)
            ) for i in range(2)
        ]

        disciplines: list[DisciplineWorksConfig] = [
            DisciplineWorksConfig(
                full_name=f'test_discipline_name_{i}',
                short_name='tdn',
                path_to_test='any_path',
                path_to_answer='any_path',
                language='python',
                works=discipline_work
            ) for i in range(3)
        ]

        disciplines_config: DisciplinesConfig = DisciplinesConfig(
            disciplines=disciplines
        )

        return disciplines_config

    @pytest.fixture
    def json_file_path(self) -> Path:
        path = Path.cwd().joinpath('tests')

        with open(path.joinpath('config.json'), 'w') as fp:
            fp.write(disciplines_json)
        json_file_path = path.joinpath('config.json')

        return json_file_path

    @pytest.fixture
    def error_json_file_path(self) -> str:
        path = Path.cwd().joinpath('tests')

        with open(path.joinpath('error_config.json'), 'w') as fp:
            fp.write(error_disciplines_json)
        error_json_file_path = path.joinpath('error_config.json')

        return error_json_file_path

    @pytest.fixture
    def disciplines_json(self) -> str:
        return disciplines_json

    @pytest.fixture
    def error_disciplines_json(self) -> str:
        return error_disciplines_json

    @pytest.fixture
    def discipline_works_json(self):
        return discipline_works_json

    @pytest.fixture
    def error_discipline_works_json(self):
        return error_discipline_works_json

    @pytest.fixture
    def discipline_works_config(self) -> str:
        works: list[DisciplineWork] = [
            DisciplineWork(
                number=i+1, amount_tasks=5, deadline=date(2020, 11, 28)
            ) for i in range(2)
        ]

        discipline_works_config: DisciplineWorksConfig = DisciplineWorksConfig(
            full_name='python_programming',
            short_name='PP',
            path_to_test='path_to_test',
            path_to_answer='path_to_answer',
            language='python',
            works=works
        )

        return discipline_works_config

    @pytest.fixture
    def delete_all_files(self):
        yield
        # удаляем все созданные раннее файлы
        path = Path.cwd().joinpath('tests')
        config_file = path.joinpath('config.json')
        error_config_file = path.joinpath('error_config.json')

        if os.path.isfile(config_file):
            os.remove(config_file)
        if os.path.isfile(error_config_file):
            os.remove(error_config_file)


class HomeWorkUtils:
    @pytest.fixture
    def discipline_home_works_json(self):
        return discipline_home_works_json

    @pytest.fixture
    def error_discipline_home_works_json(self):
        return error_discipline_home_works_json

    @pytest.fixture
    def discipline_home_works(self):
        tasks: list[HomeTask] = [
            HomeTask(number=i+1) for i in range(5)
        ]

        discipline_home_works: DisciplineHomeWorks = DisciplineHomeWorks(
            home_works=[
                HomeWork(
                    number=i+1,
                    deadline="2020-11-28",
                    tasks=tasks
                ) for i in range(2)
            ]
        )

        return discipline_home_works


class ExcelParser:
    file_path = Path.cwd().joinpath('tests').joinpath(
        'test_utils'
    ).joinpath('_teachers_students_data.xlsx')

    @pytest.fixture
    def students(self):
        parser: ExcelDataParser = ExcelDataParser(
            file_path=self.file_path,
            parse_type=ParserType.STUDENT
        )
        return parser.students

    @pytest.fixture
    def teachers(self):
        parser: ExcelDataParser = ExcelDataParser(
            file_path=self.file_path,
            parse_type=ParserType.TEACHER
        )
        return parser.teachers

    @pytest.fixture
    def teachers_and_students(self) -> tuple[
        dict[str, dict[str, list[TeacherRaw | StudentRaw]]]
    ]:
        parser: ExcelDataParser = ExcelDataParser(
            file_path=self.file_path,
            parse_type=ParserType.ALL
        )
        return parser.teachers, parser.students


class UnzipHomeWorkFiles:
    ...
