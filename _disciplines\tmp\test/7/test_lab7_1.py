from unittest import mock

import lab7_1


task = 1
error_text = 'Неправильная сумма'


def test_lab7_1(capsys, logger):
    input_data = [
        ['91', '90', '26'],
        ['2', '90', '-3'],
        ['4', '6', '9'],
    ]

    for data in input_data:
        in_data = data[:]
        try:
            with mock.patch('builtins.input', lambda: in_data.pop()):
                lab7_1.app()
                captured = capsys.readouterr()
                assert captured.out == str(int(data[0]) + int(data[1]) + int(data[2])) + "\n"
                logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')