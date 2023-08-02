import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv() # загрузка токена Tg бота

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
#dp: Dispatcher = Dispatcher(storage=storage)