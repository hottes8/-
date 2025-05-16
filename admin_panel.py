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

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

async def admin_login(message: types.Message):
    await AdminStates.waiting_password.set()
    await message.answer("🔐 Введите пароль для входа в админ-панель:",
                         reply_markup=types.ReplyKeyboardRemove())

async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.finish()
        await message.answer("👨‍💻 Вы вошли в админ-панель",
                             reply_markup=kb_admin)
    else:
        await message.answer("❌ Неверный пароль. Попробуйте снова или /cancel")

async def exit_admin_panel(message: types.Message):
    await message.answer("Вы вышли из админ-панель",
                         reply_markup=kb_menu)

async def change_order_status_start(message: types.Message):
    await AdminStates.waiting_user_id.set()
    await message.answer("Введите ID пользователя:",
                         reply_markup=types.ReplyKeyboardRemove())

async def process_user_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ ID должен быть числом. Попробуйте снова")
        return

    async with state.proxy() as data:
        data['user_id'] = message.text

    await AdminStates.next()
    await message.answer("Выберите новый статус:",
                         reply_markup=kb_statuses)

async def process_new_status(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data['user_id']
        new_status = message.text

    if db.update_order_status(user_id, new_status):
        await message.answer(f"✅ Статус заказа {user_id} изменен на '{new_status}'",
                             reply_markup=kb_admin)
    else:
        await message.answer("❌ Не удалось изменить статус",
                             reply_markup=kb_admin)

    await state.finish()