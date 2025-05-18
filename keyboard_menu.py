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
        [
            KeyboardButton(text='FAQ'),
        ],
    ],
    resize_keyboard=True
)

kb_size = InlineKeyboardMarkup(row_width=2)
kb_size.add(
    InlineKeyboardButton("1x1 м", callback_data="size_1x1"),
    InlineKeyboardButton("1x3 м", callback_data="size_1x3"),
    InlineKeyboardButton("3x5 м", callback_data="size_3x5"),
    InlineKeyboardButton("5x5 м", callback_data="size_5x5"),
    InlineKeyboardButton("10x5 м", callback_data="size_10x5"),
    InlineKeyboardButton("10x8 м", callback_data="size_10x8"),
    InlineKeyboardButton("15x10 м", callback_data="size_15x10"),
    InlineKeyboardButton("Другой размер", callback_data="size_custom"),
)

kb_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Изменить статус заказа')],
        [KeyboardButton(text='Настройка цен')],
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

faq_questions = [
    "Какой срок изготовления?",
    "Какие материалы используются?",
    "Как оплатить заказ?",
    "Какие способы доставки?",
    "Можно ли вернуть товар?",
    "Как получить скидку?"
]

kb_faq = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=faq_questions[0]),
            KeyboardButton(text=faq_questions[1]),
        ],
        [
            KeyboardButton(text=faq_questions[2]),
            KeyboardButton(text=faq_questions[3]),
        ],
        [
            KeyboardButton(text=faq_questions[4]),
            KeyboardButton(text=faq_questions[5]),
        ],
        [
            KeyboardButton(text="Вернуться в меню"),
        ]
    ],
    resize_keyboard=True
)

kb_back_from_faq = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться к вопросам")]],
    resize_keyboard=True
)