import os
from shutil import rmtree
from zipfile import ZipFile
import pytest
from pathlib import Path


class CheckExistTestFolder:
    @pytest.fixture
    def out_dir(self):
        # директория, куда будут помещаться распакованные файлы
        out_dir = 'out'
        out_dir = Path.cwd().joinpath('tests').joinpath(out_dir)
        Path.mkdir(out_dir, parents=True, exist_ok=True)
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
