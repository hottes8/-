from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='О нас'),
            KeyboardButton(text='Отмена'),
        ],
        [
            KeyboardButton(text='Сделать заказ'),
            KeyboardButton(text='Статус заказа'),
        ],
    ],
    resize_keyboard=True
)

kb_size = InlineKeyboardMarkup(row_width=2)
kb_size.add(
    InlineKeyboardButton("1x1 м", callback_data="size_1x1"),
    InlineKeyboardButton("1x2 м", callback_data="size_1x2"),
    InlineKeyboardButton("2x2 м", callback_data="size_2x2"),
    InlineKeyboardButton("3x4 м", callback_data="size_3x4"),
    InlineKeyboardButton("4x6 м", callback_data="size_4x6"),
    InlineKeyboardButton("5x10 м", callback_data="size_5x10"),
    InlineKeyboardButton("6x12 м", callback_data="size_6x12"),
    InlineKeyboardButton("Другой размер", callback_data="size_custom"),
)

kb_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Изменить статус заказа')],
        [KeyboardButton(text='Выйти из админ-панели')],
    ],
    resize_keyboard=True
)

statuses = [
    "Заказ создан",
    "В обработке",
    "В производстве",
    "Готов к выдаче",
    "Выполнен",
    "Отменен"
]

kb_statuses = ReplyKeyboardMarkup(resize_keyboard=True)
for status in statuses:
    kb_statuses.add(KeyboardButton(text=status))