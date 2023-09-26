from unittest import mock

import lab7_4


task = 4
error_text = 'Неправильный расчет выражения'


def test_lab7_4(capsys, logger):
    input_data = [
        ['9', '3'],
        ['2', '18'],
        ['4', '6'],
    ]

    for data in input_data:
        in_data = data[:]
        try:
            with mock.patch('builtins.input', lambda: in_data.pop()):
                lab7_4.app()
                captured = capsys.readouterr()
                val2, val1 = list(map(int, data))
                assert captured.out == str((val1 * 3 + val1) / 4 - val2) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')