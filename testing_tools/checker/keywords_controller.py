"""Модуль предназначен для анализа файлов-ответов студентов -
наличие или отсутвию в них ключевых слов
"""

import glob
import json
import os
import re
from pathlib import Path

from model.pydantic.test_settings import (
    TestSettings, TestLocalSettings, TestGlobalSettings
)


class KeyWordsController:
    """
    Класс применяющий политики тестирования работы к
    присланным ответам студента и откланяющий те файлы ответов,
    которые не удовлетворяют условиям (наличие импорта, наличие или отсутствие
    ключевых слов)
    """

    def __init__(self, path_to_folder: Path) -> None:

        self.test_dir = path_to_folder
        self.file_path = path_to_folder.joinpath('settings.json')
        with open(self.file_path, encoding='utf-8') as file:
            data = json.load(file)
        self.test_settings = TestSettings(**data)
        self.rejected_files: list[str] = []
        self.is_test_available = False

    def run(self) -> None:
        glv = self.test_settings.global_level  # настройки глобального уровня
        llv = self.test_settings.local_level  # настройки локального уровня
        # список всех путей файлов-ответов
        filter_test_dir = Path(self.test_dir)
        filter_test_dir = filter_test_dir.joinpath('lab*.py')
        answer_files = glob.glob(f'{filter_test_dir}')

        # проверка глобальных политик тестирования в ответах студента
        if self.__has_global_keywords(answer_files, glv):
            answer_files = glob.glob(f'{filter_test_dir}')

        self.__delete_local_settings(answer_files)
        self.__has_local_keywords(answer_files, llv)

        answer_files = glob.glob(f'{filter_test_dir}')
        if answer_files:
            self.is_test_available = True

    def has_file_for_test(self) -> bool:
        return self.is_test_available

    def has_rejected_files(self) -> bool:
        return len(self.rejected_files) > 0

    def get_rejected_file_names(self) -> list[str]:
        return self.rejected_files

    def __delete_local_settings(self, lab_files: list[str]) -> None:
        """
        Метод очистки локальных политик от отклоненных ответов студента

        :param lab_files: список оставшихся файлов ответов
        """
        lab_numbers = [self.get_lab_number(file) for file in lab_files]
        del_local_settings = []
        for it in self.test_settings.local_level:
            if it.lab_number not in lab_numbers:
                del_local_settings.append(it)

        for it in del_local_settings:
            self.test_settings.local_level.remove(it)

        del del_local_settings

    def __has_global_keywords(
            self,
            lab_files: list[str],
            global_level: TestGlobalSettings
    ) -> bool:
        """
        Метод проверки глобальных политик тестирования на ответах студента

        :param lab_files: список оставшихся файлов ответов
        :param global_level: структура, содержащая данные о глобальных
        политиках тестирования

        :return: True, если имеются отклоненные файлы на проверку, иначе False
        """
        rejected: set[str] = set()
        # если имеются глобальные запреты:
        if global_level.prohibition is not None:
            # добавлем в rejected множество отклоненных ответов студентов
            # из-за глобальных запретов
            rejected.update(
                self.__search_keywords(
                    lab_files,
                    global_level.prohibition
                )
            )
        # если имеются глобальные ограничения
        if global_level.restriction is not None:
            # добавлем в rejected множество отклоненных ответов студентов
            # из-за отсутствия в них назначенных преподом ключевых слов
            rejected.update(
                self.__search_keywords(
                    lab_files,
                    global_level.restriction,
                    is_restriction=True
                )
            )

        # удаляем те ответы студентов, которые не прошли проверку
        # на ключевые слова
        if len(rejected) > 0:
            for it in rejected:
                self.__delete_answer_and_test(it)
            return True
        return False

    def __delete_answer_and_test(self, answer_file_name: str) -> None:
        """
        Метод удаления файла ответа студента и теста к нему

        :param answer_file_name: удаляемый ответ студента

        :return: None
        """
        del_file = Path(answer_file_name)
        self.rejected_files.append(del_file.name)
        os.remove(self.test_dir.joinpath(f'test_{del_file.name}'))
        os.remove(del_file)

    def __has_local_keywords(
            self,
            lab_files: list[str],
            local_level: list[TestLocalSettings]) -> None:
        """
        Метод проверки локальных политик тестирования на ответах студента

        :param lab_files: список оставшихся файлов ответов
        :param local_level: структура, содержащая данные о локальных политиках
        тестирования для каждого из загруженного студентом задания

        :return: None
        """
        rejected: set[str] = set()
        for locset in local_level:
            for file in lab_files:
                if locset.lab_number == self.get_lab_number(file):
                    if locset.prohibition is not None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                locset.prohibition
                            )
                        )

                    if locset.restriction is not None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                locset.restriction,
                                is_restriction=True
                            )
                        )

                    # если использование импортов запрещено,
                    # то делаем проверку в ответах студентах
                    # на отсутвстие в них импортов
                    if locset.resolve_import is None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                ['import']
                            )
                        )
                    # в противном случае построчно проверяем каждую строку
                    # файла-ответа студента, есть ли там данный импорт
                    else:
                        with open(file, 'r') as lab:
                            for line in lab:
                                if re.match(
                                    r'^from\s+[\w.]+\s+import\s+[\w, ]+', line
                                ) or re.match(
                                    r'^import\s+[\w.]+[\s,]+', line
                                ):
                                    is_use = False
                                    for rx in locset.resolve_import:
                                        if re.search('^from ' + rx, line) or \
                                                re.search(
                                                    '^import ' + rx, line
                                                ):
                                            # перечисление модулей
                                            # через запятую запрещено
                                            if not re.search(
                                                '^import ' + rx+',', line
                                            ):
                                                is_use = True  # Успех!
                                            break
                                    # если нет импорта указанного
                                    # в locset.resolve_import,
                                    # то добавляем данный файл-ответ в rejected
                                    if not is_use:
                                        rejected.add(file)
        if len(rejected) > 0:
            for it in rejected:
                self.__delete_answer_and_test(it)

    def __search_keywords(
            self,
            lab_files: list[str],
            keywords: list[str],
            is_restriction=False
    ) -> set[str]:
        """
        Метод поиска запрещенных или разрешенных ключевых слов
        в ответах студента

        :param lab_files: список путей до ответов студента
        :param lab_files: список искомых ключевых слов
        :param is_restriction: Режим работы поиска.
        False - запрет ключевых слов, иначе на их обязательное присутствие

        :return: множество отклоненных ответов студента на дальнейшую проверку
        """
        rejected: set[str] = set()
        for file in lab_files:
            for it in keywords:
                with open(file, 'r') as lab:
                    content = lab.read()
                    regex = re.compile(it)
                    if bool(regex.search(content)):
                        if is_restriction:
                            continue
                        else:
                            rejected.add(file)
                            break
                    else:
                        if is_restriction:
                            rejected.add(file)
                            break
        return rejected

    def get_lab_number(self, file: str) -> int:
        """
        Функция извлечения номера задачи из строки к нему

        :param file: путь до файла с ответом

        :return: номер задачи
        """
        name = Path(file).name
        value = name.split("_")[-1]
        value = value.split('.')[0]
        return int(value)
