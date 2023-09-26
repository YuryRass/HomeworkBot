import lab7_5


task = 5
error_text = 'Неправильное деление'


def test_lab7_5(capsys, logger):
    input_data = [
        185,
        664,
        224,
    ]

    for data in input_data:
        try:
            lab7_5.app(data)
            captured = capsys.readouterr()
            assert captured.out == str(data // 4) + "\n"
            logger.add_successful_task(task)
        except AssertionError as aerr:
            logger.add_fail_task(task, error_text)
        except Exception as ex:
            logger.add_fail_task(task, 'Что-то пошло не так... Оо')