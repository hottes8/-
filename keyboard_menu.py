from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='О нас'),
            KeyboardButton(text='Отмена'),
        ],
        [
            KeyboardButton(text='start'),
        ],
        [
            KeyboardButton(text='Соси'),
            KeyboardButton(text='Соси'),
            KeyboardButton(text='Соси'),
        ]
    ],
    resize_keyboard=True
)