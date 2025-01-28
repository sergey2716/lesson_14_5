from aiogram import Bot,Dispatcher,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from crud_functions_14_5 import *

import sqlite3

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage = MemoryStorage())

kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "Информация"),
            KeyboardButton(text="Рассчитать")
        ],
        [KeyboardButton(text="Купить")]
    ], resize_keyboard= True
)


kb2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")]
    ]
)

kb3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Product_A", callback_data="product_buying"),
            InlineKeyboardButton(text="Product_B", callback_data="product_buying"),
            InlineKeyboardButton(text="Product_C", callback_data="product_buying"),
            InlineKeyboardButton(text="Product_D", callback_data="product_buying")
        ]
    ]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands= ['start'])
async def starter(message):
    await message.answer('Привет! Я бот.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('На текущий момент я пока только могу рассчитать необходимое количество килокалорий (ккал) '
                         'в сутки для каждого конкретного человека. \n По формулуe Миффлина-Сан Жеора, разработанной '
                         'группой американских врачей-диетологов под руководством докторов Миффлина и Сан Жеора. \n'
                         'А ещё пробую создать меню покупок продуктов для здоровья')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;'
                              '\nдля женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Данные необходимо вводить целыми числами')
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    mans = (10*int(data['weight'])+6.25*int(data['growth'])-5*int(data['age'])+5)
    wumans = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161)
    await message.answer(f'При таких параметрах норма калорий: \nдля мужчин {mans} ккал в сутки \nдля женщин {wumans} ккал в сутки')
    await UserState.weight.set()
    await state.finish()



@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in get_all_products():
        number = i[0]
        title = i[1]
        description = i[2]
        price = i[3]
        with open (f'{str(number) + ".jpg"}', 'rb') as img:
            await message.answer_photo(img, caption=f'Название: {title} | Описание: {description} | Цена: {price}')

    await message.answer(text='Выберите продукт для покупки: ', reply_markup=kb3)



@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer(text='Вы успешно приобрели продукт!')
    await call.answer()



# ---------------- Регистрация пользователя -------------------
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    await state.update_data(username=message.text)
    data = await state.get_data()

    name = is_included(data['username'])
    if name is True:
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    print(data)
    add_user(data['username'], data['email'], data['age'])
    await message.answer("Регистрация прошла успешно!")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
