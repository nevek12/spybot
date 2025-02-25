from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

class TextFilter(BaseFilter):
    async def __call__(self, message: Message):
        return message.text != '' and all(c.isalpha() or c.isspace() for c in message.text)


class IsSpyFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        if data['spy'] == callback.from_user.id and callback.data not in data['usernames']:
            return {'text': 'Шпион выиграл' if callback.data == data['cur_location'] else 'Шпион проиграл'}
        return False

class IsPlaying(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        return callback.from_user.id not in data['users_id']

class IsVoicingFinished(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        if callback.data not in data['locations'] and callback.from_user.id not in data['is_voice']:
            data['is_voice'].append(callback.from_user.id)
            data['is_spy'].append(callback.data)
            await state.update_data(data=data)
            return sorted(data['is_voice']) == sorted(data['users_id'])

class IsVoicing(BaseFilter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        return callback.from_user.id in data['is_voice'] and callback.data not in data['locations']
