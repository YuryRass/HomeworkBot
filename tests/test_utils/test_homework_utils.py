import pytest
from pydantic import ValidationError

from utils.homework_utils import (
    create_homeworks, homeworks_from_json,
    homeworks_to_json
)
from conftest import DisciplinesUtils, HomeWorkUtils


class TestHomeWorkUtils(DisciplinesUtils, HomeWorkUtils):
    def test_create_homeworks(
        self, discipline_works_config, discipline_home_works
    ):
        assert create_homeworks(
            discipline_works_config
        ) == discipline_home_works

    def test_homeworks_from_json(
        self, discipline_home_works_json, discipline_home_works,
        error_discipline_home_works_json
    ):
        assert homeworks_from_json(
            discipline_home_works_json
        ) == discipline_home_works

        with pytest.raises(ValidationError):
            assert homeworks_from_json(
                error_discipline_home_works_json
            ) == discipline_home_works

    def test_homeworks_to_json(
        self, discipline_home_works_json,
        discipline_home_works, error_discipline_home_works_json
    ):
        assert homeworks_to_json(
            discipline_home_works
        ) == discipline_home_works_json
