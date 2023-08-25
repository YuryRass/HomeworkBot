import pytest
from pydantic import ValidationError

from conftest import DisciplinesUtils
from utils.disciplines_utils import (
    load_disciplines_config, disciplines_config_to_json,
    disciplines_works_to_json, disciplines_works_from_json,
    counting_tasks
)


class TestDisciplinesUtils(DisciplinesUtils):
    pytestmark = pytest.mark.usefixtures("delete_all_files")

    def test_load_disciplines_config(
        self, disciplines_config, json_file_path, error_json_file_path
    ):
        assert load_disciplines_config(json_file_path) == disciplines_config

        with pytest.raises(ValidationError):
            assert load_disciplines_config(
                error_json_file_path
            ) == disciplines_config

    def test_disciplines_config_to_json(
        self, disciplines_config, disciplines_json
    ):
        assert disciplines_config_to_json(
            disciplines_config
        ) == disciplines_json

    def test_disciplines_works_to_json(
        self, discipline_works_config, discipline_works_json
    ):

        assert disciplines_works_to_json(
            discipline_works_config
        ) == discipline_works_json

    def test_disciplines_works_from_json(
        self, discipline_works_config, discipline_works_json,
        error_discipline_works_json
    ):
        assert disciplines_works_from_json(
            discipline_works_json
        ) == discipline_works_config

        with pytest.raises(ValidationError):
            assert disciplines_works_from_json(
                error_discipline_works_json
            ) == discipline_works_config

    def test_counting_tasks(self, discipline_works_config):
        assert counting_tasks(discipline_works_config) == 10
