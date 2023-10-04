"""Модуль с настройками проекта"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL configs
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_ADDRESS: str
    PSQL_PORT: int

    # Names of databases
    MAIN_DB: str
    QUEUE_DB: str

    # Telegram Bot configs
    BOT_TOKEN: str
    PATH_TO_DISCIPLINES_DATA: str
    PATH_TO_INITIALIZATION_DATA: str
    REMOTE_CONFIGURATION: bool
    DEFAULT_ADMIN: int
    TEMP_REPORT_DIR: str
    STUDENT_UPLOAD_LIMIT: int
    STUDENT_COMMAND_LIMIT: int
    FLOOD_MIDDLEWARE: bool
    AMOUNT_DOKER_RUN: int

    # DEV or TEST
    MODE: str

    @property
    def MAIN_DB_URL(self):
        return \
            'postgresql+asyncpg://' + \
            f'{self.PSQL_USER}:{self.PSQL_PASSWORD}@' + \
            f'{self.PSQL_ADDRESS}:{self.PSQL_PORT}/{self.MAIN_DB}'

    @property
    def QUEUE_DB_URL(self):
        return \
            'postgresql+asyncpg://' + \
            f'{self.PSQL_USER}:{self.PSQL_PASSWORD}@' + \
            f'{self.PSQL_ADDRESS}:{self.PSQL_PORT}/{self.QUEUE_DB}'

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


if __name__ == "__main__":
    print(Settings().model_dump())
