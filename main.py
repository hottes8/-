from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import config
from database import *
import re
import requests
import os
from keyboard_menu import kb_menu, kb_size
from aiogram import Bot, Dispatcher, types
from admin_panel import (
    AdminStates,
    admin_login,
    process_admin_password,
    exit_admin_panel,
    change_order_status_start,
    process_user_id,
    process_new_status
)

STANDARD_PRICES = {
    "1x1": 1000,
    "1x3": 2145,
    "3x5": 9900,
    "5x5": 15125,
    "10x5": 30250,
    "10x8": 37840,
    "15x10": 59400
}
PRICE_PER_M2 = 396


def calculate_price(size_str):
    """Рассчитывает стоимость баннера"""
    if size_str in STANDARD_PRICES:
        return STANDARD_PRICES[size_str]

    if "x" in size_str:
        try:
            width, height = map(float, size_str.split('x'))
            area = width * height

            if width > 15 or height > 10 or area > 150:
                return round(area * PRICE_PER_M2)

            for standard in ["1x1", "1x3", "3x5", "5x5", "10x5", "10x8", "15x10"]:
                std_w, std_h = map(float, standard.split('x'))
                if width <= std_w and height <= std_h:
                    return STANDARD_PRICES[standard]

            return STANDARD_PRICES["15x10"]
        except:
            return None
    return None



os.makedirs('photos', exist_ok=True)

db = Database()
print(db.connect())

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()


async def on_startup(_):
    print('Бот запущен')


class Form(StatesGroup):
    fio = State()
    email = State()
    phone = State()
    photo = State()
    size = State()

dp.register_message_handler(admin_login, commands=['admin'])
dp.register_message_handler(process_admin_password, state=AdminStates.waiting_password)
dp.register_message_handler(exit_admin_panel, text='Выйти из админ-панели')
dp.register_message_handler(change_order_status_start, text='Изменить статус заказа')
dp.register_message_handler(process_user_id, state=AdminStates.waiting_user_id)
dp.register_message_handler(process_new_status, state=AdminStates.waiting_new_status)

@dp.message_handler(commands=['start'])  # Регистр не важен
async def cool_command(message: types.Message):
    await message.answer(
        "Здравствуйте, вас приветствует бот для помощи заказа рекламных баннеров, в появившеемся ниже меню вы можете выбрать одну из команд.",
        reply_markup=kb_menu)


@dp.message_handler(text=['О нас'])
async def cool_command(message: types.Message):
    await message.answer('''О компании «Пе4атниковЪ»

    Если Вы заинтересованы в том, чтобы , дав рекламу, заявить о себе, привлечь новых клиентов и новых деловых партнеров, дать мощный толчок своему бизнесу, то Вы точно являетесь нашим потенциальным заказчиком. Наша компания специализируется на современных и наиболее эффективных видах рекламы, реализуя рекламные проекты различного масштаба по одним из самых низких цен в России.

    У нас вы можете заказать полиграфическую продукцию и бизнес-сувениры любой сложности и любого объема: листовки, плакаты, буклеты, каталоги, афиши, папки, прайсы, календари, конверты, пакеты, крафт-пакеты и многое другое.

    Мы имеем большой опыт в создании различных видов наружной рекламы: таблички, штендеры, вывески, объемные буквы, баннеры, растяжки, стенды, оформление витрин, световые короба, пресс-воллы.

    Наша компания производит печать на всех видах текстильных изделий: майки, куртки, футболки, бейсболки, ленты и многое другое.
                         ''')


@dp.message_handler(text=['Сделать заказ'])
async def cmd_start(message: types.Message):
    await Form.fio.set()
    await message.answer("Пожалуйста, введите ваше ФИО:")


@dp.message_handler(text=['Отмена'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer("❌ Все действия отменены", reply_markup=kb_menu)


@dp.message_handler(state=Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text
    await Form.next()
    await message.answer("Запомнил! Теперь введите ваш email:")


@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip().lower()

    if not re.fullmatch(r'^[\w.-]+@([\w-]+\.)+(ru|com)$', email):
        await message.answer(
            "❌ Email должен содержать:\n"
            "• Символ @\n"
            "• Домен, заканчивающийся на .ru или .com\n\n"
            "<b>Примеры правильных email:</b>\n"
            "• ivanov@gmail.com\n"
            "• petrov@yandex.ru\n"
            "• sidorov@sub.domain.com\n"
            "• test-2024@my-site.ru",
            parse_mode="HTML"
        )
        return

    async with state.proxy() as data:
        data['email'] = email

    await Form.next()
    await message.answer("✅ Email принят! Теперь введите ваш номер телефона:")


@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.text

    cleaned_number = re.sub(r'[^\d+]', '', phone_number)

    mobile_pattern = r'''
        ^                # Начало строки
        (\+7\d{10}       # +7 и 10 цифр (12 символов)
        |8\d{10}         # 8 и 10 цифр (11 символов)
        |9\d{9})$        # 9 и 9 цифр (10 символов)
    '''.strip()

    if not re.fullmatch(mobile_pattern, cleaned_number, re.VERBOSE):
        await message.answer(
            "❌ Пожалуйста, введите **мобильный** номер телефона:\n"
            "• В формате `+7XXXXXXXXXX` (11 цифр)\n"
            "• Или `8XXXXXXXXXX` (11 цифр)\n"
            "• Или `9XXXXXXXXX` (10 цифр)\n\n"
            "_Примеры: +79161234567, 89161234567, 9131234567_",
            parse_mode="Markdown"
        )
        return

    async with state.proxy() as data:
        data['phone'] = cleaned_number

    await Form.next()
    await message.answer("Теперь отправьте ваше фото:")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.photo)
async def process_photo(message: types.Message, state: FSMContext):
    try:

        photo = message.photo[-1]

        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{config.TOKEN}/{file.file_path}"

        response = requests.get(file_url)
        if response.status_code == 200:
            filename = f"photos/{photo.file_id}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)

            async with state.proxy() as data:
                data['photo_id'] = photo.file_id
                data['photo_url'] = file_url
                data['local_path'] = filename

            await Form.next()
            await message.answer("📏 Выберите размер баннера:", reply_markup=kb_size)
        else:
            await message.answer("❌ Не удалось загрузить фото. Попробуйте ещё раз.")
            return

    except Exception as e:
        print(f"Ошибка при обработке фото: {e}")
        await message.answer("❌ Произошла ошибка при обработке фото. Попробуйте ещё раз.")


@dp.callback_query_handler(lambda c: c.data.startswith('size_'), state=Form.size)
async def process_size(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    size_type = callback_query.data.split('_')[1]

    if size_type == "custom":
        await bot.send_message(callback_query.from_user.id,
                               "✏️ Введите размер в формате ШxВ (например 2x3 или 7x5):")
        return

    size_str = f"{size_type.replace('x', 'x')} м"
    price = calculate_price(size_type)

    async with state.proxy() as data:
        data['size'] = size_str
        data['price'] = price

    user_data = await state.get_data()

    db.save_user(
        callback_query.from_user.id,
        user_data['fio'],
        user_data['email'],
        user_data['phone'],
        user_data['photo_id'],
        user_data['photo_url'],
        user_data['local_path'],
        user_data['size'],
        user_data.get('price', 0)
    )

    await bot.send_photo(
        chat_id=callback_query.from_user.id,
        photo=user_data['photo_id'],
        caption=f"""
            📋 <b>Ваш заказ принят!</b>
            🚀 <b>Статус:</b> Заказ создан
            💰 <b>Стоимость:</b> {price} руб

            👤 <b>ФИО:</b> {user_data['fio']}
            📧 <b>Email:</b> {user_data['email']}
            📱 <b>Телефон:</b> {user_data['phone']}
            📏 <b>Размер баннера:</b> {user_data['size']}

            🖼 <i>Прикрепленное фото будет использовано для макета</i>
            """,
        parse_mode="HTML",
        reply_markup=kb_menu
    )
    await state.finish()


@dp.message_handler(state=Form.size)
async def process_custom_size(message: types.Message, state: FSMContext):
    try:

        size_text = message.text.lower().replace(' ', '').replace('м', '')

        if 'x' in size_text:
            width, height = map(float, size_text.split('x'))
            size_str = f"{width}x{height} м"
            price = calculate_price(size_text)

            if price is None:
                raise ValueError("Неверный формат размера")

            async with state.proxy() as data:
                data['size'] = size_str
                data['price'] = price

            user_data = await state.get_data()

            success = db.save_user(
                message.from_user.id,
                user_data['fio'],
                user_data['email'],
                user_data['phone'],
                user_data['photo_id'],
                user_data['photo_url'],
                user_data['local_path'],
                user_data['size'],
                user_data['price']
            )

            if success:
                caption = f"""
                    📋 <b>Ваш заказ принят!</b>
                    🚀 <b>Статус:</b> Заказ создан
                    💰 <b>Стоимость:</b> {price} руб
                    {"🟢 <i>Расчет по цене 396 руб/кв.м</i>" if (width > 6 or height > 12) else ""}

                    👤 <b>ФИО:</b> {user_data['fio']}
                    📧 <b>Email:</b> {user_data['email']}
                    📱 <b>Телефон:</b> {user_data['phone']}
                    📏 <b>Размер баннера:</b> {user_data['size']}

                    🖼 <i>Прикрепленное фото будет использовано для макета</i>
                """
                await message.answer_photo(
                    photo=user_data['photo_id'],
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=kb_menu
                )
            else:
                await message.answer("❌ Ошибка сохранения данных", reply_markup=kb_menu)

            await state.finish()

    except Exception as e:
        print(f"Ошибка обработки кастомного размера: {e}")
        await message.answer(
            "❌ Неверный формат размера. Введите в формате 'ШxВ' (например '2x3' или '7x10')",
            reply_markup=kb_menu
        )


@dp.message_handler(state=Form.size)
async def process_custom_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text


@dp.message_handler(state=Form.photo, content_types=types.ContentTypes.ANY)
async def invalid_content(message: types.Message):
    await message.reply("❌ Пожалуйста, отправьте фото!")

@dp.message_handler(text=['Статус заказа'])
async def check_order_status(message: types.Message):
    status = db.get_order_status(message.from_user.id)
    if status:
        await message.answer(f"📊 <b>Текущий статус вашего заказа:</b> {status}", parse_mode="HTML")
    else:
        await message.answer("ℹ️ У вас нет активных заказов. Хотите сделать новый?", reply_markup=kb_menu)

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def unknown_command(message: types.Message):
    if message.content_type != 'Отмена' or 'start' or 'О нас' or 'Сделать заказ':
        await message.reply("⚠️ Извините, такой команды не существует.\nИспользуйте кнопки меню или /start")
    else:
        await message.reply("❌ Я работаю только с текстовыми командами")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)