from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from homeworkbot.middlewares import BanMiddleware, StudentFloodMiddleware
from tests.test_homeworkbot.mocked_bot import MockedBot
from config import settings

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объект бота и диспетчера
bot: Bot | None = None
if settings.MODE == 'test':
    bot = MockedBot()
else:
    bot: Bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
dispatcher: Dispatcher = Dispatcher()

# устанавливаем промежуточное ПО для забаненных студентов
dispatcher.message.middleware(BanMiddleware())


# устанавливаем промежуточн. ПО для лимитирования запросов студентов
if settings.FLOOD_MIDDLEWARE:
    dispatcher.message.middleware(
        StudentFloodMiddleware(
            settings.STUDENT_UPLOAD_LIMIT,
            settings.STUDENT_COMMAND_LIMIT
        )
    )
