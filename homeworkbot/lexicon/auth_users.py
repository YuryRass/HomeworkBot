"""Выражения телеграм-бота при авторизации tg пользователей"""

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

    # коллбэки:
    STUDENT_ANSWER_YES_CALLBACK = auto()
    STUDENT_ANSWER_NO_CALLBACK = auto()

    # ответ бота на отриц. решение студента
    # о передаче своих персональных данных
    BOT_ANSWER_ON_STUDENT_DISAGREEMENT = auto()

    # сообщение от бота на ввод ФИО студентом
    BOT_MESSAGE_FOR_INPUT_STUDENT_FULL_NAME = auto()

    # успешная авторизация студента
    STUDENT_AUTH_SUCCESS = auto()


#  словарь с сообщениями бота при аутентифкации Tg пользователя
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
    BotAuthUsers.STUDENT_BUTTON_NO: 'Нет',
    BotAuthUsers.BOT_ANSWER_ON_STUDENT_DISAGREEMENT: 'Жаль! Если передумаете - перезапустите бота!',
    BotAuthUsers.BOT_MESSAGE_FOR_INPUT_STUDENT_FULL_NAME: 'Спасибо! Удачной учебы!\n'
                                                          'Для вашей идентификации введите ФИО:',
    BotAuthUsers.STUDENT_AUTH_SUCCESS: 'Поздравляю! Вы успешно авторизовались!'

}

bot_auth_callbacks: dict = {
    BotAuthUsers.STUDENT_ANSWER_YES_CALLBACK: 'start_yes',
    BotAuthUsers.STUDENT_ANSWER_NO_CALLBACK: 'start_no',
}


class BotAuthErrors(Enum):
    INCORRECT_CALLBACK_DATA = auto()
    INCORECT_STUDENT_FULLNAME = auto()
    NOT_FULL_NAME = auto()
    UNKNOWN_CALLBACK_DATA = auto()


bot_auth_errors: dict = {
    BotAuthErrors.INCORRECT_CALLBACK_DATA: 'Неизвестный формат для обработки данных!',
    BotAuthErrors.INCORECT_STUDENT_FULLNAME: 'Пожалуйста, проверьте корректность ввода ФИО '
                                          'или свяжитесь с преподавателем',
    BotAuthErrors.NOT_FULL_NAME: 'Пожалуйста, введите полное ФИО! Например: Иванов Иван Иванович',
    BotAuthErrors.UNKNOWN_CALLBACK_DATA : 'Неизвестный формат для обработки данных!'
}
