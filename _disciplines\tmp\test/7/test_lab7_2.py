from unittest import mock

import lab7_2


task = 2
error_text = 'Неправильное произведение'


def test_lab7_2(capsys, logger):
    input_data = [
        '91',
        '-3',
        '9',
    ]

    for data in input_data:
        try:
            with mock.patch('builtins.input', lambda: data):
                lab7_2.app()
                captured = capsys.readouterr()
                assert captured.out == str(int(data) * 10) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')
