"""Модуль реализует CRUD-операции с таблицей Rejected"""

import json

from pydantic.json import pydantic_encoder

from database.queue_db.database import Session
from model.pydantic.test_rejected_files import TestRejectedFiles
from model.queue_db.rejected import Rejected


def add_record(
        user_tg_id: int,
        chat_id: int,
        rejected: TestRejectedFiles
) -> None:
    """Добавление записи в таблицу Rejected.

    Args:
        user_tg_id (int): ID телеграм пользователя.

        chat_id (int): ID телеграм чата.

        rejected (TestRejectedFiles): pydantic модель с файлами,
    которые не прошли тесты.
    """
    session = Session()

    json_data = json.dumps(
        rejected,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(',', ': '),
        default=pydantic_encoder
    )

    session.add(
        Rejected(
            telegram_id=user_tg_id,
            chat_id=chat_id,
            data=json_data
        )
    )
    session.commit()
    session.close()


def is_empty() -> bool:
    """Пуста ли таблица Rejected.

    Returns:
        bool: True, если таблица пуста.
    """
    with Session() as session:
        data = session.query(Rejected).first()
        return data is None


def is_not_empty() -> bool:
    """Есть ли записи в таблице Rejected.

    Returns:
        bool: True, если записи есть в таблице.
    """
    with Session() as session:
        data = session.query(Rejected).first()
        return data is not None


def get_first_record() -> Rejected:
    """Получение первой записи из таблицы Rejected.
    После чего происходит удаление записи из таблицы.

    Returns:
        Rejected: запись из таблицы Rejected.
    """
    with Session() as session:
        record = session.query(Rejected).first()
        session.query(Rejected).filter(
            Rejected.id == record.id
        ).delete(synchronize_session='fetch')
        session.commit()
        return record