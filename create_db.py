from utils import conn_context, db_path

with conn_context(db_path) as conn:
    curs = conn.cursor()
    curs.executescript(
        '''CREATE TABLE IF NOT EXISTS Objects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE);

        CREATE TABLE IF NOT EXISTS Devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        ip TEXT NOT NULL UNIQUE,
        id_object INTEGER,
        CONSTRAINT devices_name_ip_id_object UNIQUE(name, ip, id_object),
        FOREIGN KEY (id_object) REFERENCES objects (id));

        CREATE TABLE IF NOT EXISTS Favorites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_chat TEXT,
        id_object INTEGER,
        CONSTRAINT favorites_id_chat_id_object_uq UNIQUE(id_chat, id_object),
        FOREIGN KEY (id_object) REFERENCES objects (id));

        CREATE TABLE IF NOT EXISTS Track(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_chat TEXT,
        track INT);
        '''
    )