from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import Database
from keyboard_menu import kb_admin, kb_statuses, kb_menu
from dotenv import load_dotenv
import os

load_dotenv()
db = Database()

class AdminStates(StatesGroup):
    waiting_password = State()
    waiting_user_id = State()
    waiting_new_status = State()
    waiting_price_action = State()
    waiting_new_price = State()
    waiting_custom_price = State()

async def get_standard_prices():
    """Получает стандартные цены из базы"""
    prices = db.get_prices()
    return {p['size']: p['price'] for p in prices if not p['is_custom']}

async def get_custom_price():
    """Получает цену за м² из базы"""
    prices = db.get_prices()
    for p in prices:
        if p['is_custom']:
            return p['price']
    return 396

async def admin_login(message: types.Message):
    await AdminStates.waiting_password.set()
    await message.answer("🔐 Введите пароль для входа в админ-панель:",
                         reply_markup=types.ReplyKeyboardRemove())

async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text == os.getenv('ADMIN_PASSWORD'):
        await state.finish()
        await message.answer("👨‍💻 Вы вошли в админ-панель",
                             reply_markup=kb_admin)
    else:
        await message.answer("❌ Неверный пароль. Попробуйте снова или /cancel")

async def price_settings(message: types.Message):
    await AdminStates.waiting_price_action.set()
    standard_prices = await get_standard_prices()

    kb_sizes = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in standard_prices.keys():
        kb_sizes.add(types.KeyboardButton(text=size))
    kb_sizes.add(types.KeyboardButton(text="Цена за м²"))
    kb_sizes.add(types.KeyboardButton(text="Назад"))

    await message.answer(
        "📊 Выберите размер для изменения цены:",
        reply_markup=kb_sizes
    )

async def process_price_action(message: types.Message, state: FSMContext):
    standard_prices = await get_standard_prices()

    if message.text in standard_prices:
        async with state.proxy() as data:
            data['size'] = message.text
            data['is_custom'] = False

        await AdminStates.waiting_new_price.set()
        await message.answer(
            f"Текущая цена для {message.text}: {standard_prices[message.text]} руб\n"
            "Введите новую цену:",
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text == "Цена за м²":
        custom_price = await get_custom_price()
        await AdminStates.waiting_custom_price.set()
        await message.answer(
            f"Текущая цена за м²: {custom_price} руб\n"
            "Введите новую цену за квадратный метр:",
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text == "Назад":
        await state.finish()
        await message.answer("👨‍💻 Админ-панель", reply_markup=kb_admin)
    else:
        await message.answer("❌ Неверный размер. Попробуйте снова")

async def process_new_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError

        async with state.proxy() as data:
            size = data['size']
            is_custom = data.get('is_custom', False)

        success = db.update_price(size, price, is_custom)

        if success:
            await message.answer(
                f"✅ Цена для размера {size} изменена на {price} руб",
                reply_markup=kb_admin
            )
        else:
            await message.answer("❌ Ошибка сохранения", reply_markup=kb_admin)

    except ValueError:
        await message.answer("❌ Введите корректную сумму (целое число больше 0)")
    finally:
        await state.finish()

async def process_custom_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError

        if db.update_price('custom', price, is_custom=True):
            await message.answer(
                f"✅ Цена за м² изменена на {price} руб",
                reply_markup=kb_admin
            )
        else:
            await message.answer("❌ Ошибка сохранения", reply_markup=kb_admin)
    except ValueError:
        await message.answer("❌ Введите корректную сумму (целое число больше 0)")
    finally:
        await state.finish()

async def exit_admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("👋 Вы вышли из админ-панели", reply_markup=kb_menu)

async def change_order_status_start(message: types.Message):
    await AdminStates.waiting_user_id.set()
    await message.answer("Введите ID пользователя:", reply_markup=types.ReplyKeyboardRemove())

async def process_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        async with state.proxy() as data:
            data['user_id'] = user_id
        await AdminStates.next()
        await message.answer("Выберите новый статус:", reply_markup=kb_statuses)
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")

async def process_new_status(message: types.Message, state: FSMContext):
    statuses = ["Заказ создан", "В обработке", "В производстве", "Готов к выдаче", "Выполнен", "Отменен"]
    if message.text not in statuses:
        await message.answer("❌ Выберите статус из предложенных")
        return

    async with state.proxy() as data:
        user_id = data['user_id']

    if db.update_order_status(user_id, message.text):
        await message.answer(f"✅ Статус заказа пользователя {user_id} изменен на: {message.text}",
                             reply_markup=kb_admin)
    else:
        await message.answer("❌ Ошибка обновления статуса", reply_markup=kb_admin)

    await state.finish()