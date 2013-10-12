import sqlite3
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)
DATABASE = '/home/ferran/WebApps/ToDo/database'

class Connection:
	def __enter__(self):
		self.conn = sqlite3.connect(DATABASE)
		return self.conn.cursor()

	def __exit__(self, type, value, traceback):
		self.conn.commit()
		self.conn.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/todo/<list_id>')
def todo(list_id):
	with Connection() as c:
		c.execute('SELECT todo, done, id FROM item WHERE list_id=(?)', (list_id,))
		todo = c.fetchall()
	return render_template('todo.html', todo=todo, list_id=list_id)

@app.route('/add/<list_id>', methods=['POST'])
def add_item(list_id):
	text = request.form['todo']
	with Connection() as c:
		c.execute('INSERT INTO item (list_id, todo, done) VALUES (?, ?, 0)', (list_id, text,))
	return redirect(url_for('todo', list_id=list_id))

@app.route('/mark/<item_id>', methods=['POST'])
def mark(item_id):
	with Connection() as c:
		c.execute('UPDATE item SET done=1 WHERE id=?', item_id)

@app.route('/unmark/<item_id>', methods=['POST'])
def unmark(item_id):
	with Connection() as c:
		c.execute('UPDATE item SET done=0 WHERE id=?', item_id)

if __name__ == '__main__':
	app.debug = True
	app.run()