"""Модуль с настройками проекта"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_NAME: str
    QUEUE_DB_NAME: str
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

    MODE: str

    @property
    def MAIN_DB_URL(self):
        return f'sqlite:///{self.DATABASE_NAME}.sqlite'

    @property
    def QUEUE_DB_URL(self):
        return f'sqlite:///{self.QUEUE_DB_NAME}.sqlite'

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


if __name__ == "__main__":
    print(Settings().model_dump())
