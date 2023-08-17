"""Модуль реализует CRUD-операции с промежуточной таблицей QueueOut"""

import json

from pydantic.json import pydantic_encoder

from database.queue_db.database import Session
from model.pydantic.queue_out_raw import TestResult
from model.queue_db.queue_out import QueueOut


def is_empty() -> bool:
    """Проверка на пустоту таблицы QueueOut.

    Returns:
        bool: True, если таблица пустая.
    """
    with Session() as session:
        data = session.query(QueueOut).first()
        return data is None


def is_not_empty() -> bool:
    """Проверяет таблицу QueueOut на наличие в ней записей.

    Returns:
        bool: True, если таблица непустая.
    """
    with Session() as session:
        data = session.query(QueueOut).first()
        return data is not None


def get_all_records() -> list[QueueOut]:
    """Возвращает список всех записей таблицы QueueOut.

    Returns:
        list[QueueOut]: список записей таблицы QueueOut.
    """
    with Session() as session:
        return session.query(QueueOut).all()


def delete_record(record_id: int) -> None:
    """Удаление записи по ее ID в таблице QueueOut.

    Args:
        record_id (int): ID записи.
    """
    with Session() as session:
        session.query(QueueOut).filter(
            QueueOut.id == record_id
        ).delete(synchronize_session='fetch')
        session.commit()


def add_record(user_tg_id: int, chat_id: int, data: TestResult) -> None:
    """Добавление записи в таблицу QueueOut.

    Args:
        user_tg_id (int): ID телеграм пользователя.
        chat_id (int): ID телеграм чата.
        data (TestResult): pydantic-данные о результататх тестирования.
    """

    session = Session()

    # конвертируем pydantic данные в JSON формат
    json_data = json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(',', ': '),
        default=pydantic_encoder
    )

    session.add(
                QueueOut(
                    telegram_id=user_tg_id,
                    chat_id=chat_id,
                    data=json_data
                )
            )
    session.commit()
    session.close()