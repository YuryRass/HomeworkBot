from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from homeworkbot.configuration import bot

import database.main_db.common_crud as common_crud
import database.main_db.student_crud as student_crud
from database.main_db.common_crud import UserEnum


router: Router = Router()


class AuthStates(StatesGroup):
    full_name = State()


async def is_subscribed(chat_id: int, user_id: int) -> bool:
    """
        Возвращает True, если пользователь с идентификатором = user_id
        присутствует в Telegram чате с идентификатором = chat_id
        Параметры:
        chat_id (int): Telegram ID чата (группы).
        user_id (int): Telegram ID пользователя.
    """
    try:
        # получаем информацию об участнике (пользователе) Tg-чата
        response = await bot.get_chat_member(chat_id, user_id)

        # если пользователь покинул чат
        if response.status == 'left':
            return False
        # если пользователь присутсвует
        else:
            return True
    except TelegramAPIError as ex:
        if ex.message == 'Bad Request: user not found':
            return False


@router.message(CommandStart())
async def process_start_command(message: Message):
    """
        Хэндлер, срабатывающий на команду '\start'
    """

    # Происходит проверка какой группе принадлежит пользователь
    # (админ, препод, студент). Если студент еще не ввел свои
    # персональные данные, то он не окажется в таблице Students.
    # В таком случае Tg-бот предложет пользователю дать согласие
    # на обработку его персональных данных. Если пользователь еще
    # не подписан на Tg-канал, то бот выведет соответсвующее сообщение,
    # чтобы пользователь подписался на канал.
    user = common_crud.user_verification(message.from_user.id)
    match user:
        case UserEnum.Admin:
            await message.answer(
                text='<b>О, мой повелитель! Бот готов издеваться над студентами!!!</b>',
                # TODO: клавиатура
            )
        case UserEnum.Teacher:
            await message.answer(
                text='Приветствую! Надеюсь, что в этом году студенты вас не разочаруют!',
                # TODO: клавиатура
            )
        case UserEnum.Student:
            await message.answer(
                text='С возвращением! О, юный падаван ;)',
                # TODO: клавиатура
            )
        case _:
            chats = common_crud.get_chats()
            user_in_chat = False
            for chat_id in chats:
                user_in_chat = await is_subscribed(chat_id, message.from_user.id)
                if user_in_chat:
                    break

            if user_in_chat:
                # создаем инлаин-кнопки | Да | Нет| для пользователя
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton('Да', callback_data='start_yes'),
                    InlineKeyboardButton('Нет', callback_data='start_no'),
                )

                text = 'Бот осуществляет хранение и обработку персональных данных '
                text += 'на российских серверах. К таким данным относятся: \n'
                text += '- ФИО\n'
                text += '- Успеваемость по предмету\n'
                text += 'Telegram ID\n'
                text += 'Вы даете разрешение на хранение и обработку своих персональных данных?'
                await message.answer(
                    text=text,
                    reply_markup=markup,
                )
            else:
                await message.answer(
                    text='Пожалуйста, подпишитесь на канал!!!',
                )

@router.callback_query(lambda call: 'start_' in call.data,
                       StateFilter(default_state))
async def callback_auth_query(call: CallbackQuery, state: FSMContext):
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'start':
            if call.data == 'start_yes':
                text = 'Спасибо! Удачной учебы!\n'
                text += 'Для вашей идентификации введите ФИО:'
                await call.answer(text=text)

                # Устанавливаем состояние ожидания ввода ФИО
                await state.set_state(AuthStates.full_name)

            if call.data == 'start_no':
                await call.answer(
                    text='Жаль! Если передумаете - перезапустите бота!',
                )
        case _:
            await call.answer(
                text='Неизвестный формат для обработки данных!',
            )


@router.callback_query(StateFilter(AuthStates.full_name))
async def input_full_name(message: Message, state: FSMContext):
    full_name = message.text
    if len(full_name.split(' ')) != 3:
        await message.answer(
           text='Пожалуйста, введите полное ФИО! Например: Иванов Иван Иванович'
        )
    else:
        # если студент с такими ФИО уже есть в таблице Student,
        # то обновляем его Telegram ID
        if student_crud.has_student(full_name):
            student_crud.set_telegram_id(full_name, message.from_user.id)
            await message.answer(
                text='Поздравляю! Вы успешно авторизовались!',
                # TODO: клавиатура
            )
            # очищаем состояние
            await state.clear()
        # некорректный ввод ФИО
        else:
            await message.answer(
                text='Пожалуйста, проверьте корректность ввода ФИО ' +
                'или свяжитесь с преподавателем'
            )