from unittest import mock

import lab7_3


task = 3
error_text = 'Неправильное возведение в степень'


def test_lab7_3(capsys, logger):
    input_data = [
        ['9', '3'],
        ['2', '10'],
        ['4', '6'],
    ]

    for data in input_data:
        in_data = data[:]
        try:
            with mock.patch('builtins.input', lambda: in_data.pop()):
                lab7_3.app()
                captured = capsys.readouterr()
                assert captured.out == str(int(data[1]) ** int(data[0])) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')