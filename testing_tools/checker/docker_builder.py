"""Модуль отвечает за создание докер образа и запуск докер-контейнера"""

import json
import uuid
from pathlib import Path

from python_on_whales import docker, Volume

from model.pydantic.test_settings import TestSettings


class DockerBuilder:
    """
    Класс формирования Dockerfile
    """

    def __init__(
        self, path_to_folder: Path, student_id: int, lab_number: int
    ) -> None:
        # добавить data_path - путь до хостовой директории куда будут попадать данные из контейнера
        """
        :param path_to_folder: путь до директории с файлами, которые будут
        отправлены в контейнер
        :param student_id: id студента
        :param lab_number: номер лабораторной (домашней) работы
        """
        self.test_dir = path_to_folder
        settings_path = path_to_folder.joinpath('settings.json')
        with open(settings_path, encoding='utf-8') as file:
            data = json.load(file)
        self.dependencies = TestSettings(**data).dependencies
        self.tag_name = f'{student_id}-{lab_number}-{uuid.uuid4()}'
        self.report_data: str | None = None

        # Docker volume
        self.data_path = Path.cwd().joinpath('docker_data').joinpath(self.tag_name)
        Path(self.data_path).mkdir(parents=True, exist_ok=True)

    def _build_docker_file(self):
        file = [
            "FROM python:3.11\n",
            "WORKDIR /opt/\n"
            "RUN mkdir data\n",
            "RUN pip install pytest pydantic\n",
        ]

        if self.dependencies:
            file.append(f"RUN pip install {' '.join(self.dependencies)}\n")

        file.append("COPY . /opt\n")

        # --tb=no - никаких сообщений
        file.append('CMD ["pytest", "--tb=no"]\n')

        f = open(self.test_dir.joinpath('Dockerfile'), "w")
        f.writelines(file)
        f.close()

    def get_run_result(self) -> str:
        return self.report_data

    def run_docker(self):
        self._build_docker_file()
        # создаем докер том с названием = self.tag_name
        some_volume = docker.volume.create(self.tag_name)

        docker.build(
            context_path=self.test_dir, tags=self.tag_name
        )
        docker.run(
            self.tag_name, name=self.tag_name, detach=True,
            volumes=[(some_volume, "/opt/data")]
        )
        self.report_data = self.get_json_data_from_volume(some_volume)

    def get_json_data_from_volume(self, volume: Volume) -> str:
        docker.volume.copy((volume, '.'), self.data_path)
        for fname in self.data_path.iterdir():
            if fname.name.endswith('.json'):
                return fname.read_text(encoding='utf-8')
