from unittest import mock

import lab7_7


task = 7
error_text = 'Неправильное значение выражения'


def test_lab7_7(capsys, logger):
    input_data = [
        ['91', '98', '26'],
        ['2', '90', '-3'],
        ['4', '6', '9'],
    ]

    for data in input_data:
        in_data = data[:]
        try:
            with mock.patch('builtins.input', lambda: in_data.pop()):
                lab7_7.app()
                captured = capsys.readouterr()
                val3,  val2, val1 = list(map(int, data))
                assert captured.out == str((val1 + val2) / (val2 - val3)) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')