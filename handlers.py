from aiogram import types, filters, Dispatcher
from utils import (
    add_object, add_device,
    get_list_of_objects, add_to_fav, show_status, show_status_detail)


dp = Dispatcher()
kb = [
        [types.KeyboardButton(text='/help')],
        [types.KeyboardButton(text='/status')],
        [types.KeyboardButton(text='/status_detail')],
]
keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
    one_time_keyboard=True)


@dp.message(filters.Command(commands=['start']))
async def cmd_start(message: types.Message):
    await message.answer(
        'Приветствую! Я PingBot - бот, который поможет в отслеживании '
        'состояния устройств в вашей сети!', reply_markup=keyboard)


@dp.message(filters.Command(commands=['help']))
async def cmd_help(message: types.Message):
    await message.answer(
        'Что я умею?\n'
        '/add_obj - добавить группу устройст\n'
        '/add_device - добавить устройство в группу\n'
        '/add_fav - группу в избранное для отслеживания\n'
        '/status_detail - посмотреть статус устройств по группам\n'
        '/status - посмотреть состояние групп')


@dp.message(filters.Command(commands=['add_obj']))
async def cmd_add_obj(message: types.Message, command: filters.CommandObject):
    if command.args:
        await add_object(command.args, message)
    else:
        await message.answer(
            'Пожалуйста, укажите название обьекта после команды /add_obj!'
        )


@dp.message(filters.Command(commands=['add_device']))
async def cmd_add_device(
    message: types.Message,
    command: filters.CommandObject
):
    if command.args:
        await add_device(command.args, message)
    else:
        await message.answer(
            'Пожалуйста, укажите устройство в формате "имя_устройства ip '
            'id_обьекта" после команды /add_device!'
        )
        await get_list_of_objects(message)


@dp.message(filters.Command(commands=['add_fav']))
async def add_fav(message: types.Message, command: filters.CommandObject):
    if command.args:
        await add_to_fav(command.args, message)
    else:
        await message.answer(
            'Пожалуйста, укажите id обьекта после /add_fav!'
        )
        await get_list_of_objects(message)


@dp.message(filters.Command(commands=['status_detail']))
async def status_detail(message: types.Message):
    await show_status_detail(message)


@dp.message(filters.Command(commands=['status']))
async def status(message: types.Message):
    await show_status(message)
