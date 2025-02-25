import logging
from copy import deepcopy

from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import yes_no_kb, is_user_play_kb
from lexicon.lexicon import LEXICON
from FSM.FSM import FSM

# Инициализируем логгер
logger = logging.getLogger(__name__)

user_router = Router()

# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@user_router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON['start_game'], reply_markup=yes_no_kb)
    logger.info('в process_start_command handler')

@user_router.message(Command(commands='clear'))
async def cmd_clear(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        logger.debug(message.json())
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.chat.id, i)

    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        logger.debug(f"Все сообщения {message.chat.id} удалены")
    logger.info('в cmd_clear handler')
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@user_router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text[0:-13]])
    logger.info('в process_help_command handler')

#при согласии на игру запрос на то кто будет играть
@user_router.callback_query(F.data == 'yes')
async def process_write_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text=LEXICON['is_user_play'], reply_markup=is_user_play_kb)
    await state.set_state(FSM.write_user)
    await state.update_data(data={'users_id': [], 'usernames': [], 'users_finished': [], 'know_role_id': [], 'is_spy': [], 'is_voice': [], 'locations': []})
    data = await state.get_data()
    logger.info('в process_write_user handler')
    logger.debug(data)

@user_router.callback_query(F.data == 'no')
async def process_no_playing(callback: CallbackQuery, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(callback.message.message_id, 0, -1):
            await bot.delete_message(callback.message.chat.id, i)

    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        logger.debug(f"Все сообщения {callback.message.chat.id} удалены")
    logger.info('в process_no_playing handler')