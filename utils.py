import asyncio
import logging
import sqlite3
from contextlib import contextmanager

from aiogram import Bot, types
from pythonping import ping

TEMP_STATUS = {}
TEMP_TRACK = {}
TEMP_SND_ERROR = {}
db_path = 'device_object.db'


@contextmanager
def conn_context(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


async def update_status(bot: Bot) -> None:
    while True:
        TEMP_STATUS.clear()
        TEMP_TRACK.clear()
        with conn_context(db_path) as conn:
            curs = conn.cursor()
            await get_all_fav_objects(curs)
            try:
                curs.execute('''
                SELECT *
                FROM Objects
                ''')
            except sqlite3.OperationalError:
                continue
            all_objects = curs.fetchall()
            for object in all_objects:
                all_devices = await get_object_devices(object, curs)
                temp_object_devices = await status_check(
                    all_devices, bot, object)
                TEMP_STATUS[object['name']] = temp_object_devices
        logging.info('UPDATE')
        await asyncio.sleep(10)


async def status_check(devices: list, bot: Bot, object: sqlite3.Row) -> list:
    msg = ''
    temp_object_devices = []
    for device in devices:
        device_response = ping(device['ip'], size=32, count=4)
        temp = []
        temp.append(device['name'])
        try:
            if device_response.stats_packets_returned == 0:
                temp.append('\U0001F7E5')  # DOWN
                for chat_id in TEMP_TRACK[object['name']]:
                    if device['name'] not in TEMP_SND_ERROR:
                        msg = (
                            'Отсутствует соединение \n' +
                            f"{object['name']}: {device['name']}" +
                            ' \U0001F440\n')
                        TEMP_SND_ERROR[device['name']] = [chat_id]
                        await bot.send_message(chat_id, msg)
            else:
                if device['name'] in TEMP_SND_ERROR:
                    for chat_id in TEMP_SND_ERROR[device['name']]:
                        msg = (
                            "Восстановление соединения с " +
                            f"{object['name']}: {device['name']}" +
                            ' \U0001F44D')
                        await bot.send_message(chat_id, msg)
                    TEMP_SND_ERROR.pop(device['name'])
                temp.append('\U0001F7E9')
                temp.append(
                    str(device_response.rtt_avg_ms) + ' мс')
        except KeyError:
            logging.info('Нет отслеживаемых обьектов!')
        temp_object_devices.append(temp)
    return temp_object_devices


async def get_all_fav_objects(curs: sqlite3.Cursor) -> None:
    curs.execute('''
        SELECT id_chat
        FROM track
        WHERE track=1;
        ''')
    track_chat = curs.fetchall()
    for chat in track_chat:
        curs.execute(f'''
        SELECT o.name as name, f.id_chat as id_chat
        FROM favorites as f
        LEFT JOIN objects as o ON o.id = f.id_object
        WHERE f.id_chat = {chat['id_chat']}
        ORDER BY name;
        ''')
    fav_track_objects = curs.fetchall()
    for object in fav_track_objects:
        if object['name'] in TEMP_TRACK:
            TEMP_TRACK[object['name']].append(object['id_chat'])
        else:
            TEMP_TRACK[object['name']] = [object['id_chat']]


async def add_object(args: str, message: types.Message) -> None:
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


async def add_device(args: str, message: types.Message) -> None:
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


async def add_to_fav(args: str, message: types.Message) -> None:
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
        except TypeError:
            await message.reply('Несуществующий ID!')
        else:
            conn.commit()
            await message.reply(f'{object_name} добавлен в избранное!')


async def show_status_detail(message: types.Message) -> None:
    id_chat = message.chat.id
    fav_objects = await get_fav_object_from_db(id_chat)
    if len(fav_objects) == 0:
        await message.answer('Нет избранных объектов!')
    else:
        msg = ''
        for object in fav_objects:
            msg += '\U0001F539 ' + object['name'] + ':\n'
            for device in TEMP_STATUS[object['name']]:
                msg += '\U00002796 '
                msg += ' '.join(str(param) for param in device)
                msg += '\n'
        await message.answer(msg)


async def show_status(message: types.Message) -> None:
    id_chat = message.chat.id
    msg = ''
    status = ''
    fav_objects = await get_fav_object_from_db(id_chat)
    if len(fav_objects) == 0:
        await message.answer('Нет избранных объектов!')
    else:
        for object in fav_objects:
            msg += '\U0001F539 ' + object['name'] + ' '
            for device in TEMP_STATUS[object['name']]:
                if device[1] == '\U0001F7E9':
                    status = '\U0001F7E9'
                else:
                    status = '\U0001F7E5'
                    break
            msg += status + '\n'
        await message.answer(msg)


async def get_fav_object_from_db(id_chat) -> list[sqlite3.Row]:
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''
        SELECT o.name as name
        FROM favorites as f
        LEFT JOIN objects as o ON o.id = f.id_object
        WHERE f.id_chat = "{id_chat}";''')
        fav_objects = curs.fetchall()
        return fav_objects


async def add_remove_track(message: types.Message) -> None:
    id_chat = message.chat.id
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute(f'''
        SELECT id_chat, track
        FROM track
        WHERE id_chat = "{id_chat}";''')
        chat_track = curs.fetchall()
        if len(chat_track) == 0:
            curs.execute(f'''
            INSERT INTO track (id_chat, track)
            VALUES ('{id_chat}', 1);''')
            conn.commit()
            await message.answer(
                'Теперь вам будут приходить уведомления, '
                'если что-то пойдёт не так.')
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
                await message.answer('Я уведомлю Вас, если что-то случится!')


async def get_list_of_objects() -> list[sqlite3.Row]:
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        curs.execute('''SELECT * FROM objects;''')
        rows = curs.fetchall()
        return rows


async def represent_list_if_objects(rows: sqlite3.Row, message: types.Message) -> None:
    all_objects_list = ''
    for row in rows:
        unpack_row = ''
        id, name = tuple(row)
        unpack_row = f'\U0001F539 {name}, ID: {id}\n'
        all_objects_list += unpack_row
    if all_objects_list == '':
        await message.answer('Список объектов пуст!')
    else:
        await message.answer(all_objects_list)


async def get_list_of_devices() -> dict:
    try:
        objects = await get_list_of_objects()
        all_objects_devices = {}
        with conn_context(db_path) as conn:
            curs = conn.cursor()
            for object in objects:
                row_device = await get_object_devices(object, curs)
                temp_devices = []
                for device in row_device:
                    temp_devices.append(device)
                if len(temp_devices) == 0:
                    all_objects_devices[object['name']] = 'Нет устройств!'
                else:
                    all_objects_devices[object['name']] = temp_devices
        return all_objects_devices
    except KeyError:
        logging.info("Object hasn't devices")


async def represent_list_if_devices(
    all_obj_dev: dict, message: types.Message
) -> None:
    all_devices_msg = ''
    for object, devices in all_obj_dev.items():
        all_devices_msg += f"\U0001F539 {object}\n"
        if devices == 'Нет устройств!':
            all_devices_msg += '\U00002796 Нет устройств!\n'
        else:
            for device in devices:
                all_devices_msg += '\U00002796 '
                all_devices_msg += f"ID: {device['ID']} NAME: {device['name']} IP: {device['ip']}"
                all_devices_msg += '\n'
    if all_devices_msg == '':
        await message.answer('Список устройств пуст!')
    else:
        await message.answer(all_devices_msg)


async def get_object_devices(
    object: sqlite3.Row, curs: sqlite3.Cursor
) -> list[sqlite3.Row]:
    try:
        curs.execute(f'''
        SELECT id, name, ip, id_object
        FROM devices
        WHERE id_object='{object['id']}'
        ''')
        all_devices = curs.fetchall()
        return all_devices
    except KeyError:
        logging.info("Object hasn't devices")


async def del_obj(message: types.Message, args: str) -> None:
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        if await chek_exist(args, 'objects', curs):
            curs.execute('''PRAGMA foreign_keys=on;''')
            curs.execute(f'''
            DELETE
            FROM objects
            WHERE id='{args}';''')
            conn.commit()
            await message.reply('Объект удалён!')
        else:
            await message.reply('Некорректный ID!')


async def del_dev(message: types.Message, args: str) -> None:
    with conn_context(db_path) as conn:
        curs = conn.cursor()
        if await chek_exist(args, 'devices', curs):
            curs.execute('''PRAGMA foreign_keys=on;''')
            curs.execute(f'''
            DELETE
            FROM devices
            WHERE id='{args}';''')
            conn.commit()
            await message.reply('Устройство удалёно!')
        else:
            await message.reply('Некорректный ID!')


async def chek_exist(args: str, table: str, curs: sqlite3.Cursor) -> bool:
    curs.execute(f'''
    EXIST(SELECT * FROM {table}) WHERE id='{args}') AS flag;''')
    flag = curs.fetchone()['flag']
    logging.info(f'{flag} - eto flag-------------------')
    return flag
