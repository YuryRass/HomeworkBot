import os
from distutils.util import strtobool
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from homeworkbot.middlewares import BanMiddleware, StudentFloodMiddleware

load_dotenv() # загрузка токена Tg бота

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объект бота и диспетчера
bot: Bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
dispatcher: Dispatcher = Dispatcher()

# устанавливаем промежуточное ПО для забаненных студентов
dispatcher.message.middleware(BanMiddleware())


# устанавливаем промежуточн. ПО для лимитирования запросов студентов
if bool(strtobool(os.getenv("FLOOD_MIDDLEWARE"))):
    dispatcher.message.middleware(
        StudentFloodMiddleware(
            int(os.getenv("STUDENT_UPLOAD_LIMIT")),
            int(os.getenv("STUDENT_COMMAND_LIMIT"))
        )
    )