import logging
import sqlite3
from aiogram import types
from contextlib import contextmanager
from pythonping import ping
from data_classes import Objects, Devices, Favorites

TEMP_STATUS = []
db_path = 'device_object.db'

@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


async def update_status():
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute('''
        SELECT D.id, D.name, D.ip, O.name as object_name
        FROM devices as D
        JOIN objects as O ON O.id = D.id_object''')
        all_devices = curs.fetchall()
        for device in all_devices:
            device_response = ping(device['ip'], size=32, count=4)
            temp = []
            temp.append(device['id'])
            temp.append(device['name'])
            if device_response.stats_packets_returned <= 1:
                temp.append('DOWN')
            else:
                temp.append('UP')
                temp.append(device_response.rtt_avg_ms)
            temp.append(device['object_name'])
            TEMP_STATUS.append(temp)


async def add_object(args: str, message: types.Message):
    with conn_context(db_path) as conn:
        try:
            curs = conn.cursor()
            querry = f'''INSERT INTO objects(name) VALUES('{args}');'''
            curs.execute(querry)
        except sqlite3.IntegrityError:
            await message.reply('Такой объект уже существует!')
        else:
            conn.commit()
            await message.reply('Объект успешно добавлен!')


async def add_device(args: str, message: types.Message):
    with conn_context(db_path) as conn:
        try:
            curs = conn.cursor()
            name, ip, id_object = args.split()
            curs.execute(
                f'''INSERT INTO devices(name, ip, id_object) VALUES('{name}',
                '{ip}', '{id_object}');''')
        except sqlite3.IntegrityError:
            await message.reply(
                'Устройство с таким именем или ip уже существует!')
        except ValueError:
            await message.reply(
                'Введите данные после команды /add_device в формате: '
                'имя ip id_обьекта.')
        else:
            conn.commit()
            await message.reply('Устройство успешно добавлено!')


async def add_to_fav(args: str, message: types.Message):
    id_chat = message.chat.id
    object_name = ''
    with conn_context(db_path) as conn:
        try:
            curs = conn.cursor()
            curs.execute(f'''INSERT INTO favorites(id_chat, id_object)
                             VALUES('{id_chat}','{args}');''')
            curs.execute(f'''SELECT name FROM objects WHERE id='{args}';''')
            object_name = curs.fetchone()['name']
        except sqlite3.IntegrityError:
            await message.reply(f'{object_name} уже в избранном!')
        else:
            conn.commit()
            await message.reply(f'{object_name} добавлен в избранное!')


async def show_status(message: types.Message):
    # id_chat = message.chat.id
    msg = ''
    for device in TEMP_STATUS:
        msg += ' '.join(map(str, device))
        msg += '\n'
    await message.answer(msg)


async def ping_devices(args: str, message: types.Message):
    name = args
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''SELECT ip FROM devices WHERE name='{name}';''')
        device_ip = curs.fetchone()['ip']
        response_list = ping(device_ip, size=32, count=4)
        await message.answer(
            f'Среднее время отклика {response_list.rtt_avg_ms} мсек')


async def get_list_of_devices(message: types.Message):
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute('''SELECT * FROM devices;''')
        rows = curs.fetchall()
        all_devices_list = ''
        curs.execute('''SELECT * FROM objects;''')
        for row in rows:
            unpack_row = ''
            id, name, ip, id_object = tuple(row)
            curs.execute(
                f'''SELECT object FROM objects WHERE id='{id_object}';''')
            object = curs.fetchone()['name']
            unpack_row = f'id:{id}, name:{name}, ip:{ip}, object:{object}\n'
            all_devices_list += unpack_row
        await message.answer(all_devices_list)


async def get_list_of_objects(message: types.Message):
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute('''SELECT * FROM objects;''')
        rows = curs.fetchall()
        all_objects_list = ''
        for row in rows:
            unpack_row = ''
            id, name = tuple(row)
            unpack_row = f'id:{id}, name:{name}\n'
            all_objects_list += unpack_row
        await message.answer(all_objects_list)


# async def show_fav_status(message: types.Message):
#     id_chat = message.chat.id
#     with conn_context(db_path) as conn:
#         curs = conn.cursor()
#         curs.execute(f'''SELECT * FROM favorites WHERE id_chat='{id_chat}';''')
#         all_obj_fav = curs.fetchall()
#         all_devices = []
#         for obj in all_obj_fav:
#             curs.execute(
#                 f'''SELECT * FROM devices WHERE '''
#                 f'''id_object='{obj['id_object']}';''')
#             devices_object = curs.fetchall()
#             for device in devices_object:
#                 id, name, ip, id_object = tuple(device)
#                 curs.execute(
#                     f'''SELECT name FROM objects WHERE '''
#                     f'''id='{obj[id_object]}';''')
#                 current_object = curs.fetchone()
#                 all_devices.append([id, name, ip, current_object])
#         status = ''
#         for device in all_devices:
#             response_list = ping(device[2], size=32, count=4)
#             status += (f'id:{device[0]}, name:{device[1]}, ip:{device[2]}, '
#                        f'object:{device[3]}, время отклик - '
#                        f'{response_list.rtt_avg_ms} мсек\n')
#         await message.answer(status)


# async def get_list_fav_obj(id_chat: str):
#     with conn_context(db_path) as conn:
#         curs = conn.cursor()
#         curs.execute(f'''SELECT id_object FROM favorites WHERE id_chat='{id_chat}';''')
#         all_objects_for_this_chat = curs.fetchall()
#         all_devices_list = ''
#         for objects in all_objects_for_this_chat:
#             curs.execute(f'''SELECT  FROM favorites WHERE id_chat='{id_chat}';''')
#             unpack_row = ''
#             id, name = tuple(row)
#             unpack_row = f'id:{id}, name:{name}\n'
#             all_objects_list += unpack_row
#         await message.answer(all_objects_list)


async def get_list_objects():
    pass


async def get_list_device():
    pass


async def ping_all(ip: str):
    pass
