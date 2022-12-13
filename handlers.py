import logging
from aiogram import Dispatcher, filters, types

from utils import (add_device, add_object, add_remove_track, add_to_fav,
                   get_list_of_objects, show_status, show_status_detail,
                   represent_list_if_objects, get_list_of_devices,
                   represent_list_if_devices, del_obj, del_dev)

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
    logging.info(f'start chat with chat_id = {message.chat.id}')


@dp.message(filters.Command(commands=['help']))
async def cmd_help(message: types.Message):
    await message.answer(
        'Что я умею?\n'
        '/add_obj - добавить обьект\n'
        '/add_device - добавить устройство в группу обьекта\n'
        '/add_fav - добавить объект в избранное для отслеживания\n'
        '/status_detail - посмотреть статус устройств по группам\n'
        '/status - посмотреть состояние обьектов\n'
        '/trackornot - вкл/выкл уведомления\n'
        '/show_obj - показать все объекты\n'
        '/show_dev - показать все устройства\n'
        '/del_obj - удалить обьект по ID\n'
        '/del_device - удалить устройство по ID\n')
    logging.info(f'command /help for chat_id = {message.chat.id}')


@dp.message(filters.Command(commands=['add_obj']))
async def cmd_add_obj(message: types.Message, command: filters.CommandObject):
    if command.args:
        await add_object(command.args, message)
    else:
        await message.answer(
            'Пожалуйста, укажите название обьекта после команды /add_obj!'
        )
    logging.info(
        f'command /add_obj for chat_id = {message.chat.id} with args '
        f'= {command.args}')


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
        rows = await get_list_of_objects()
        await represent_list_if_objects(rows, message)
    logging.info(
        f'command /add_device for chat_id = {message.chat.id} with args '
        f'= {command.args}')


@dp.message(filters.Command(commands=['add_fav']))
async def add_fav(message: types.Message, command: filters.CommandObject):
    if command.args:
        await add_to_fav(command.args, message)
    else:
        await message.answer(
            'Пожалуйста, укажите id обьекта после /add_fav!'
        )
        rows = await get_list_of_objects()
        await represent_list_if_objects(rows, message)
    logging.info(
        f'command /add_fav for chat_id = {message.chat.id} with args '
        f'= {command.args}')


@dp.message(filters.Command(commands=['status_detail']))
async def status_detail(message: types.Message):
    logging.info(f'command /status_detail for chat_id = {message.chat.id}')
    await show_status_detail(message)


@dp.message(filters.Command(commands=['status']))
async def status(message: types.Message):
    logging.info(f'command /status for chat_id = {message.chat.id}')
    await show_status(message)


@dp.message(filters.Command(commands=['trackornot']))
async def trackornot(message: types.Message):
    logging.info(f'command /status for chat_id = {message.chat.id}')
    await add_remove_track(message)


@dp.message(filters.Command(commands=['show_obj']))
async def show_objects(message: types.Message):
    logging.info(f'command /show_obj for chat_id = {message.chat.id}')
    rows = await get_list_of_objects()
    await represent_list_if_objects(rows, message)


@dp.message(filters.Command(commands=['show_dev']))
async def show_devices(message: types.Message):
    logging.info(f'command /show_dev for chat_id = {message.chat.id}')
    obj_devices = await get_list_of_devices()
    await represent_list_if_devices(obj_devices, message)


@dp.message(filters.Command(commands=['del_obj'],))
async def del_object(message: types.Message, command: filters.CommandObject):
    logging.info(
        f'command /del_obj for chat_id = {message.chat.id} with args '
        f'= {command.args}')
    await del_obj(message, command.args)


@dp.message(filters.Command(commands=['del_device']))
async def del_device(message: types.Message, command: filters.CommandObject):
    logging.info(
        f'command /del_device for chat_id = {message.chat.id} with args '
        f'= {command.args}')
    await del_dev(message, command.args)
