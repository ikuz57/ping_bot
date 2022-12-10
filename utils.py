import logging
import sqlite3
from aiogram import types
import asyncio
from contextlib import contextmanager
from pythonping import ping


TEMP_STATUS = {}
db_path = 'device_object.db'


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


async def update_status():
    while True:
        TEMP_STATUS.clear()
        with conn_context(db_path) as conn:
            curs = conn.cursor()
            try:
                curs.execute('''
                SELECT *
                FROM Objects
                ''')
            except sqlite3.OperationalError:
                continue
            all_objects = curs.fetchall()
            for object in all_objects:
                temp_object_devices = []
                curs.execute(f'''
                    SELECT id, name, ip, id_object
                    FROM devices
                    WHERE id_object='{object['id']}'
                    ''')
                all_devices = curs.fetchall()
                for device in all_devices:
                    device_response = ping(device['ip'], size=32, count=4)
                    temp = []
                    temp.append(device['name'])
                    if device_response.stats_packets_returned <= 1:
                        temp.append('\U0001F534')  # DOWN
                    else:
                        temp.append('\U0001F7E2')
                        temp.append(str(device_response.rtt_avg_ms) + ' мс')
                    temp_object_devices.append(temp)
                TEMP_STATUS[object['name']] = temp_object_devices
        logging.info('UPDATE')
        logging.info(TEMP_STATUS)
        await asyncio.sleep(10)


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


async def show_status_detail(message: types.Message):
    id_chat = message.chat.id
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''
        SELECT o.name as name
        FROM favorites as f
        LEFT JOIN objects as o ON o.id = f.id_object
        WHERE f.id_chat = {id_chat}''')
        fav_objects = curs.fetchall()
    msg = ''
    for object in fav_objects:
        msg += object['name'] + ':\n'
        for device in TEMP_STATUS[object['name']]:
            msg += ' '.join(str(param) for param in device)
            msg += '\n'
    await message.answer(msg)


async def show_status(message: types.Message):
    id_chat = message.chat.id
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''
        SELECT o.name as name
        FROM favorites as f
        LEFT JOIN objects as o ON o.id = f.id_object
        WHERE f.id_chat = {id_chat}''')
        fav_objects = curs.fetchall()
    logging.info(fav_objects)
    msg = ''
    status = ''
    for object in fav_objects:
        msg += object['name'] + ': '
        for device in TEMP_STATUS[object['name']]:
            if device[1] == '\U0001F7E2':
                status = '\U0001F7E2'
            else:
                status = '\U0001F534'
                break
        msg += status + '\n'
    await message.answer(msg)


async def add_remove_track(message: types.Message):
    id_chat = message.chat.id
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''
        SELECT id_chat, track
        FROM track
        WHERE id_chat = {id_chat}''')
        chat_track = curs.fetchall()
        logging.info('-----------------------')
        logging.info(len(chat_track))
        logging.info('-----------------------')
        # logging.info(chat_track[0]['track'])
        if len(chat_track) == 0:
            curs.execute(f'''
            INSERT INTO track (id_chat, track)
            VALUES ('{id_chat}', 1);''')
            conn.commit()
            await message.answer('Я уведомлю вас, если что-то случится...')
        else:
            if chat_track[0]['track'] == 1:
                curs.execute(f'''
                UPDATE track
                SET track= 0
                WHERE id_chat='{id_chat}';''')
                conn.commit()
                await message.answer('Вы отключили уведомления...')
            else:
                curs.execute(f'''
                UPDATE track
                SET track = 1
                WHERE id_chat='{id_chat}';''')
                conn.commit()
                await message.answer('Я уведомлю Вас, если что-то случится...')



# async def ping_devices(args: str, message: types.Message):
#     name = args
#     with conn_context(db_path) as conn:
#         curs = conn.cursor()
#         curs.execute(f'''SELECT ip FROM devices WHERE name='{name}';''')
#         device_ip = curs.fetchone()['ip']
#         response_list = ping(device_ip, size=32, count=4)
#         await message.answer(
#             f'Среднее время отклика {response_list.rtt_avg_ms} мсек')


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


async def get_list_objects():
    pass


async def get_list_device():
    pass


async def ping_all(ip: str):
    pass
