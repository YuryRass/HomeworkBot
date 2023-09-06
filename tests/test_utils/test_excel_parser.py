from tests.test_utils.conftest import ExcelParser


class TestExcelParser(ExcelParser):
    def test_excel_parser(self, students, teachers, teachers_and_students):
        assert 'ТМП' in students.keys()
        assert 'УG-2801' in students['ТМП'].keys()
        assert len(students['ТМП']['УG-2801']) == 12
        assert students['ТМП']['УG-2801'][6].full_name == \
            'Мороз Иван Эдуардович'

        assert 'ТМП' in teachers.keys()
        assert 'УG-2801' in teachers['ТМП'].keys()
        assert len(teachers['ТМП']['УG-2801']) == 1
        assert teachers['ТМП']['УG-2801'][0].telegram_id == 591260097

        assert (teachers, students) == teachers_and_students
