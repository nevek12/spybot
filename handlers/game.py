import asyncio
import logging

import random
from collections import Counter

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from filters.filters import IsSpyFilter, IsPlaying, TextFilter, IsVoicing, IsVoicingFinished
from handlers.user import cmd_clear
from keyboards.keyboards import finish_kb, create_inline_kb, yes_no_kb
from lexicon.lexicon import LEXICON
from FSM.FSM import FSM

# Инициализируем логгер
logger = logging.getLogger(__name__)

game_router = Router()

# запись пользователей кто будет играть в
@game_router.callback_query(StateFilter(FSM.write_user), F.data == 'agree', IsPlaying())
async def process_ask_location(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['users_id'].append(callback.from_user.id)
    data['usernames'].append(callback.from_user.first_name)
    logger.debug(callback.json())
    await callback.message.answer(text=f'Записалося {callback.from_user.first_name}')

    await state.update_data(data=data)
    await callback.answer(text='ГОЛОВКА ОТ Х#*')
    logger.info('в process_ask_location handler')
    logger.debug(await state.get_data())

@game_router.callback_query(StateFilter(FSM.write_user), F.data == 'finished', ~IsPlaying())
async def process_ask_location(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text=LEXICON['choice_location'], reply_markup=finish_kb)
    await state.set_state(FSM.write_location)

# при завершение записи локаций
@game_router.message(StateFilter(FSM.write_location), F.text == 'Завершить запись') # написать фильтр что ты добавил хотя бы одну локацию
async def process_finish_write_location(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    data['users_finished'].append(message.from_user.id)
    logger.debug(data)
    logger.debug('в process_finish_write_location handler')
    if sorted(data['users_id']) == sorted(data['users_finished']):
        data['ask'] = random.choice(data['usernames'])
        data['cur_location'] = random.choice(data['locations'])
        data['spy'] = random.choice(data['users_id'])
        await cmd_clear(message, bot, state)
        await message.answer(text='узнать свою роль?', reply_markup=create_inline_kb(1, 'роль'))
        logger.info('в process_finish_write_location handler')
        logger.debug(await state.get_data())

        await state.set_state(FSM.role)
    await state.update_data(data)

# запись локации
@game_router.message(StateFilter(FSM.write_location), TextFilter())
async def process_write_location(message: Message, state: FSMContext):
    data = await state.get_data()
    loc = message.text.split('\n')
    logger.debug(message.text)
    logger.debug(loc)
    for m_t in loc:
        if m_t not in data['locations']:
            data['locations'].append(m_t)
    await state.update_data(data=data)
    logger.info('в process_write_location handler')
    logger.debug(await state.get_data())

# показывает роль и если все узнали выводит таблицу
@game_router.callback_query(StateFilter(FSM.role), F.data == 'роль')
async def process_show_role(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.from_user.id not in data['know_role_id']:
        data['know_role_id'].append(callback.from_user.id)
    if callback.from_user.id != data['spy']:
        await callback.answer(text=data['cur_location'].upper())
    else:
        await callback.answer(text='____ШПИОН____')
    await state.update_data(data=data)

    if sorted(data['know_role_id']) == sorted(data['users_id']): # не забыть переделать в set
        await callback.message.edit_text(text=f'Задает вопрос {data['ask']}', reply_markup=create_inline_kb(2, *data['locations']))
        await state.set_state(FSM.playing)
        await asyncio.sleep(10)
        state_cur = await state.get_state()
        if state_cur == FSM.playing:
            await callback.message.answer(text=LEXICON['who_is_spy'], reply_markup=create_inline_kb(2, *data['usernames']))
    logger.info('в process_show_role handler')
    logger.debug(await state.get_data())

# проверка на то что шпион выиграл или проиграл
@game_router.callback_query(StateFilter(FSM.playing), IsSpyFilter())
async def process_guess_location(callback: CallbackQuery, state: FSMContext, text):
    await callback.answer()
    await callback.message.answer(text=text)
    await callback.message.answer(text='Начать заново игру?', reply_markup=yes_no_kb)
    await state.clear()

    logger.info('в process_guess_location handler')
    logger.debug(await state.get_data())
    logger.debug(await state.get_state())

# когда пользователь еще раз нажал кнопку голосовать
@game_router.callback_query(StateFilter(FSM.playing),  IsVoicing())
async def process_repeat_voicing(callback: CallbackQuery):
    await callback.answer(text='ТЫ УЖЕ ГОЛОСОВАЛ')

#записывает голоса и проверяем на нахождение шпиона шпиона
@game_router.callback_query(StateFilter(FSM.playing),  IsVoicingFinished())
async def process_voicing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()


    counter = Counter(data['is_spy'])
    str_lsst = []
    for username, count_voice in counter.items():
        str_lsst.append(f'{username} : {count_voice}')
    await callback.message.edit_text(text='\n'.join(str_lsst))

    pot_spy = counter.most_common(1)[-1][0]
    if counter.most_common(1)[-1][-1] == counter.most_common(2)[-1][-1] and len(counter.most_common(2)) >= 2:
        await asyncio.sleep(3)
        await callback.message.answer(text='Переголосование \n\n' + LEXICON['who_is_spy'], reply_markup=create_inline_kb(2, *data['usernames']))
        data['is_voice'] = []
        data['is_spy'] = []
    else:
        if data['usernames'][data['users_id'].index(data['spy'])] == pot_spy:
            await callback.message.answer(text=f'Вы угадали шпиона - {pot_spy}\n\n{pot_spy} отгадывает локацию')
        else:
            await callback.message.answer(text=f'Вы НЕ угадали шпиона - {pot_spy}')
            await callback.message.answer(text='Начать заново игру?', reply_markup=yes_no_kb)
            await state.clear()


    await state.update_data(data=data)
    logger.info('в process_voicing handler')
    logger.debug(await state.get_data())



@game_router.callback_query(StateFilter(FSM.playing))
async def process_pressed_location_no_spy(callback: CallbackQuery):
    await callback.answer()






