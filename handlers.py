from aiogram import types, filters, Dispatcher
from utils import (
    add_object, add_device, ping_devices, get_list_of_devices,
    get_list_of_objects, add_to_fav, show_status)


dp = Dispatcher()


@dp.message(filters.Command(commands=['start']))
async def cmd_start(message: types.Message):
    await message.answer(
        'Приветствую! Я PingBot - бот, который поможет в отслеживании '
        'состоянии устройств!')


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
    await show_status(message)













# @dp.message(filters.Command(commands=['ping']))
# async def cmd_ping(message: types.Message, command: filters.CommandObject):
#     if command.args:
#         await ping_devices(command.args, message)
#     else:
#         await message.answer(
#             'Пожалуйста, укажите корректное название устройство после /ping!'
#         )
#         await get_list_of_devices(message)


# @dp.message(filters.Command(commands=['show_fav']))
# async def show_fav(message: types.Message, command: filters.CommandObject):
#     await show_fav_status(message)
