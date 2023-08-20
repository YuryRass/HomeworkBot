import pytest

import lab7_1

task_id = 1
error_text = 'Неправильная сумма'


@pytest.mark.parametrize(
    "a, b, res",
    [
        (5, 2, 8),
        (4, 6, 10),
        (5, 88, 93)
    ]
)
def test_sum(logger, a, b, res):
    try:
        assert lab7_1.sum(a, b) == res
        logger.add_successful_task(task_id)
    except AssertionError as assert_error:
        logger.add_fail_task(task_id, error_text)
    except Exception as ex:
        logger.add_fail_task(task_id, 'Что-то пошло не так :(')