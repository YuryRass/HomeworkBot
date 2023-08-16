"""Выражения телеграм-бота"""

from enum import Enum, auto

class BotAuthUsers(Enum):
    """Класс сообщений бота при аутентификации Tg пользователя"""
    HELP_MESSAGE = auto()
    STUDENT_AUTH_ANSWER = auto()
    TEACHER_AUTH_ANSWER = auto()
    ADMIN_AUTH_ANSWER = auto()
    TG_USER_NOT_IN_CHAT = auto()
    # запрос разрешения у студентов на обработку их персональных данных
    STUDENT_PERSONAL_DATA_REQUEST = auto()
    STUDENT_BUTTON_YES = auto()
    STUDENT_BUTTON_NO = auto()


class BotNotCorrectDataFormat:
    pass
# словарь с сообщениями бота при аутентифкации Tg пользователя
bot_auth_messages: dict = {
    BotAuthUsers.HELP_MESSAGE: '',
    BotAuthUsers.STUDENT_AUTH_ANSWER: 'С возвращением! О, юный падаван 😉',
    BotAuthUsers.TEACHER_AUTH_ANSWER: 'Приветствую! Надеюсь, что в этом году '
                                          'студенты вас не разочаруют!',
    BotAuthUsers.ADMIN_AUTH_ANSWER: '<b>О, мой повелитель! '
                                        'Бот готов издеваться над студентами!!!</b>',

    BotAuthUsers.STUDENT_PERSONAL_DATA_REQUEST:
                    'Бот осуществляет хранение и обработку персональных данных '
                    'на российских серверах. К таким данным относятся: \n'
                    '- ФИО\n'
                    '- Успеваемость по предмету\n'
                    'Telegram ID\n'
                    'Вы даете разрешение на хранение и обработку своих персональных данных?',

    BotAuthUsers.TG_USER_NOT_IN_CHAT: 'Пожалуйста, подпишитесь на канал!!!',
    BotAuthUsers.STUDENT_BUTTON_YES: 'Да',
    BotAuthUsers.STUDENT_BUTTON_NO: 'Нет'
}
