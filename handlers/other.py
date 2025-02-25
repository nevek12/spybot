from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.user import logger

other_router = Router()


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@other_router.callback_query()
async def send_ec(callback: CallbackQuery, state: FSMContext):
    logger.debug(callback.json())
    logger.debug(await state.get_state())
    logger.debug(await state.get_data())