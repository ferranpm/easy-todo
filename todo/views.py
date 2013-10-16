import sqlite3
import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from . import app
from . import DATABASE
from . import utils

connection = utils.Connection(DATABASE)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
	with connection as c:
		title = request.form['title']
		password = request.form['password']
		c.execute('INSERT INTO todos (title, password) VALUES (?, ?)', (title, password,))
		list_id = c.lastrowid
	return redirect(url_for('todo', list_id=list_id))

@app.route('/<list_id>')
def todo(list_id):
	with connection as c:
		c.execute('SELECT title, password FROM todos WHERE list_id=?', (list_id,))
		list_data = c.fetchone()
		if not list_data:
			return render_template('notfound.html', list_id=list_id)
		c.execute('SELECT todo, done, item_id FROM items WHERE list_id=?', (list_id,))
		todo = c.fetchall()
		data = {
				'title': list_data[0],
				'password': list_data[1],
				'todo': [{'todo':t[0], 'done':t[1], 'item_id':t[2]} for t in todo],
				'list_id': list_id
				}
	return render_template('todo.html', **data)

@app.route('/add/<list_id>', methods=['POST'])
def add_item(list_id):
	text = request.form['todo']
	with connection as c:
		c.execute('INSERT INTO items (list_id, todo, done) VALUES (?, ?, 0)', (list_id, text,))
	return redirect(url_for('todo', list_id=list_id))

@app.route('/remove/<item_id>', methods=['GET'])
def remove(item_id):
	with connection as c:
		c.execute('SELECT list_id FROM items WHERE item_id=?', (item_id,))
		list_id = c.fetchone()[0]
		c.execute('DELETE FROM items WHERE item_id=?', (item_id,))
	return redirect(url_for('todo', list_id=list_id))

@app.route('/remove_marked/<list_id>', methods=['GET'])
def remove_marked(list_id):
	with connection as c:
		c.execute('DELETE FROM items WHERE list_id=? AND done=1', (list_id,))
	return redirect(url_for('todo', list_id=list_id))

@app.route('/mark/<item_id>', methods=['POST'])
def mark(item_id):
	with connection as c:
		c.execute('UPDATE items SET done=1 WHERE item_id=?', (item_id,))
	return 'marked'

@app.route('/unmark/<item_id>', methods=['POST'])
def unmark(item_id):
	with connection as c:
		c.execute('UPDATE items SET done=0 WHERE item_id=?', (item_id,))
	return 'unmarked'

@app.route('/settitle/<list_id>', methods=['POST'])
def set_title(list_id):
	title = request.form['title']
	with connection as c:
		c.execute('UPDATE todos SET title=? WHERE list_id=?', (title, list_id,))
	return redirect(url_for('todo', list_id=list_id))
