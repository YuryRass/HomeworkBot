disciplines_json: str = '''{
    "disciplines": [
        {
            "full_name": "test_discipline_name_0",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": 1,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        },
        {
            "full_name": "test_discipline_name_1",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": 1,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        },
        {
            "full_name": "test_discipline_name_2",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": 1,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        }
    ]
}'''


error_disciplines_json: str = '''{
    "disciplines": [
        {
            "ERROR": "test_discipline_name_0",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": "ERROR",
                    "amount_tasks": 1,
                    "deadline": "ERROR"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        },
        {
            "full_name": "test_discipline_name_1",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": 1,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        },
        {
            "full_name": "test_discipline_name_2",
            "short_name": "tdn",
            "path_to_test": "any_path",
            "path_to_answer": "any_path",
            "language": "python",
            "works": [
                {
                    "number": 1,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                },
                {
                    "number": 2,
                    "amount_tasks": 2,
                    "deadline": "2020-11-28"
                }
            ]
        }
    ]
}'''


discipline_works_json: str = '''{
    "full_name": "python_programming",
    "short_name": "PP",
    "path_to_test": "path_to_test",
    "path_to_answer": "path_to_answer",
    "language": "python",
    "works": [
        {
            "number": 1,
            "amount_tasks": 5,
            "deadline": "2020-11-28"
        },
        {
            "number": 2,
            "amount_tasks": 5,
            "deadline": "2020-11-28"
        }
    ]
}'''

error_discipline_works_json: str = '''{
    "full_name": "python_programming",
    "short_name": "PP",
    "path_to_test": "path_to_test",
    "path_to_answer": "path_to_answer",
    "language": "python",
    "works": [
        {
            "number": "ERROR",
            "amount_tasks": 5,
            "deadline": "ERROR"
        },
        {
            "number": 2,
            "amount_tasks": 5,
            "deadline": "2020-11-28"
        }
    ]
}'''
