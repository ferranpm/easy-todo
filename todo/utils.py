import sqlite3
import os
from contextlib import closing
from . import DATABASE

def connect_db():
	return sqlite3.connect(DATABASE)

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()


class Connection:

	def __init__(self, path):
		self.path = path

	def __enter__(self):
		self.conn = sqlite3.connect(self.path)
		return self.conn.cursor()

	def __exit__(self, type, value, traceback):
		self.conn.commit()
		self.conn.close()
