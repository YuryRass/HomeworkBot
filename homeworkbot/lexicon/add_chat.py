from enum import Enum, auto


class BotAddChat(Enum):
    """Класс сообщений бота при добавлении tg чата"""
    INPUT_TG_ID = auto()
    ADD_CHAT_SUCCESS = auto()


class BotAddChatErrors(Enum):
    """Ошибки tg пользователя"""
    NOT_CORRECT_ID_CHAT = auto()
    NOT_NEGATIVE_ID = auto()
    NO_RIGHTS = auto()

bot_messages: dict = {
    BotAddChat.INPUT_TG_ID: "Введите telegram id добавляемого группового чата:",
    BotAddChat.ADD_CHAT_SUCCESS: "Групповой чат успешно добавлен!",
}

bot_errors: dict = {
    BotAddChatErrors.NOT_CORRECT_ID_CHAT: "Убедитесь, что вводите целое отрицательное число!",
    BotAddChatErrors.NOT_NEGATIVE_ID: "ID чата должен быть отрицательным числом!",
    BotAddChatErrors.NO_RIGHTS: "Нет прав доступа!!!"
}
