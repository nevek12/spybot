from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from lexicon.lexicon import LEXICON

# ---------------- создаем inline-клавиатуру для ответа да нет
buttons_yes_no = [InlineKeyboardButton(text='да', callback_data='yes'), InlineKeyboardButton(text='нет', callback_data='no')]

yes_no_kb_builder = InlineKeyboardBuilder()
yes_no_kb_builder.row(*buttons_yes_no, width=2)

yes_no_kb: InlineKeyboardMarkup = yes_no_kb_builder.as_markup()

# ------------------ создаем кнопку для завершения
button_finish = [KeyboardButton(text='Завершить запись')]

finish_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[button_finish], one_time_keyboard=True, input_field_placeholder="для завершения ввода локаций нажми на кнопку ниже")

# ------------------ создаем инлайнкнопку кто будет играть

button_is_user_play = [InlineKeyboardButton(text='Я', callback_data='agree'), InlineKeyboardButton(text='Кончить запись для всех', callback_data='finished')]

is_user_play_kb = InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[button_is_user_play])

#--------------------------_________________________------------
# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

