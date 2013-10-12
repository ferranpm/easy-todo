import sqlite3
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)
DATABASE = '/home/ferran/WebApps/ToDo/database'

def connect_db():
	return sqlite3.connect(DATABASE)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/todo/<list_id>')
def todo(list_id):
	conn = connect_db()
	c = conn.cursor()
	c.execute('SELECT todo, done, id FROM item WHERE list_id=(?)', (list_id,))
	todo = c.fetchall()
	conn.close()
	return render_template('todo.html', todo=todo, list_id=list_id)

@app.route('/add/<list_id>', methods=['POST'])
def add_item(list_id):
	text = request.form['todo']
	conn = connect_db()
	c = conn.cursor()
	c.execute('INSERT INTO item (list_id, todo, done) VALUES (?, ?, 0)', (list_id, text,))
	conn.commit()
	conn.close()
	url = '/todo/%s' % list_id
	return redirect(url_for('todo', list_id=list_id))

@app.route('/mark/<item_id>', methods=['POST'])
def mark(item_id):
	conn = connect_db()
	c = conn.cursor()
	c.execute('UPDATE item SET done=1 WHERE id=?', item_id)
	conn.commit()
	conn.close()

@app.route('/unmark/<item_id>', methods=['POST'])
def unmark(item_id):
	conn = connect_db()
	c = conn.cursor()
	c.execute('UPDATE item SET done=0 WHERE id=?', item_id)
	conn.commit()
	conn.close()

if __name__ == '__main__':
	app.debug = True
	app.run()
