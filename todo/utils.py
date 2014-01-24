import sqlite3
import os
from contextlib import closing
from . import DATABASE
from . import app

class Connection:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

connection = Connection(DATABASE)

def db_connect():
    return sqlite3.connect(DATABASE)

def db_init():
    with closing(db_connect()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def db_exists():
    return os.path.isfile(DATABASE)

def db_valid_todo_id(list_id):
    valid_length = len(list_id) > 0
    exists = True
    with connection as c:
        c.execute('SELECT * FROM todos WHERE list_id=?', (list_id,))
        if not c.fetchone():
            exists = False
    return not exists and valid_length

def has_password(list_id):
    with connection as c:
        c.execute('SELECT password FROM todos WHERE list_id=?', (list_id,))
        password = c.fetchone()[0]
    return len(password) > 0

def has_permission(list_id, cookies):
    password = has_password(list_id)
    hashed_password = ''
    if password:
        with connection as c:
            c.execute('SELECT password FROM todos WHERE list_id=?', (list_id,))
            hashed_password = c.fetchone()[0]
    cookie = False
    if 'password' in cookies:
        cookie = cookies['password'] == hashed_password
    return (password and cookie) or (not password)

