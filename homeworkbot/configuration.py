import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from homeworkbot.middlewares import BanMiddleware

load_dotenv() # загрузка токена Tg бота

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объект бота и диспетчера
bot: Bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
dispatcher: Dispatcher = Dispatcher()

# устанавливаем промежуточное ПО для забаненных студентов
dispatcher.message.middleware(BanMiddleware())
