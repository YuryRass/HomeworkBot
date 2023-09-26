from unittest import mock

import lab7_8


task = 8
error_text = 'Неправильный результат выражения или проблема в считывании значений'


def test_lab7_8(capsys, logger):
    input_data = [
        '1 4 12 5 1 3 4'
        '3 8 1 45 0 5 12',
        '3 0 1 4 32 1 9',
    ]

    for data in input_data:
        try:
            with mock.patch('builtins.input', lambda: data):
                lab7_8.app()
                captured = capsys.readouterr()
                my_list = list(map(int, data.split()))
                assert captured.out == str(my_list[0] + my_list[-1]) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')
