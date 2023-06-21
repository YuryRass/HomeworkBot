from environs import Env
from dataclasses import dataclass


@dataclass
class DataBase():
    database_name: str
    queue_db_name: str


@dataclass
class Config():
    db: DataBase


def load_config(path: str | None = None):
    env: Env = Env()
    env.read_env()
    config: Config = Config(db=DataBase(database_name=env('DATABASE_NAME'),
                            queue_db_name=env('QUEUE_DB_NAME')))
    return config
