from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import config
from keyboard_menu import kb_menu


bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    print('Бот запущен')


class Form(StatesGroup):
    fio = State()
    email = State()
    phone = State()



@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.fio.set()
    await message.answer("Пожалуйста, введите ваше ФИО:", reply_markup=kb_menu)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод отменен")


@dp.message_handler(state=Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text
    await Form.next()
    await message.answer("Запомнил! Теперь введите ваш email:")


@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
    await Form.next()
    await message.answer("Запомнил! Теперь введите ваш номер телефона:")


# @dp.message_handler(state=Form.phone)
# async def process_phone(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['phone'] = message.text
#         user_data = dict(data)

@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_data = data.as_dict()

    success = db.save_user(
        message.from_user.id,
        user_data['fio'],
        user_data['email'],
        message.text
    )

    # result = (
    #     "✅ Данные сохранены!\n"
    #     f"ФИО: {user_data['fio']}\n"
    #     f"Email: {user_data['email']}\n"
    #     f"Телефон: {user_data['phone']}"
    #)

    if success:
        await message.answer("✅ Данные успешно сохранены!")
    else:
        await message.answer("❌ Произошла ошибка при сохранении данных")

    await state.finish()

    # await message.answer(result)
    # await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)