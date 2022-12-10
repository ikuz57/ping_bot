from aiogram import types, filters, Dispatcher
from utils import (
    add_object, add_device, add_remove_track,
    get_list_of_objects, add_to_fav, show_status, show_status_detail)


dp = Dispatcher()
buttons = [
        [types.KeyboardButton(text='/help')],
        [types.KeyboardButton(text='/status')],
        [types.KeyboardButton(text='/status_detail')],
        [types.KeyboardButton(text='/trackornot')]
]

keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


@dp.message(filters.Command(commands=['start']))
async def cmd_start(message: types.Message):
    await message.answer(
        'Приветствую! Я PingBot - бот, который поможет в отслеживании '
        'состояния устройств в вашей сети!', reply_markup=keyboard)


@dp.message(filters.Command(commands=['help']))
async def cmd_help(message: types.Message):
    await message.answer(
        'Что я умею?\n'
        '/add_obj - добавить обьект\n'
        '/add_device - добавить устройство в группу обьекта\n'
        '/add_fav - добавить объект в избранное для отслеживания\n'
        '/status_detail - посмотреть статус устройств по группам\n'
        '/status - посмотреть состояние обьектов')


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


@dp.message(filters.Command(commands=['trackornot']))
async def trackornot(message: types.Message):
    await add_remove_track(message)
