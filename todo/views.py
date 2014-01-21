import os
import random
import sqlite3
import string
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import make_response
from . import app
from . import DATABASE
from . import utils
from . import security

connection = utils.Connection(DATABASE)

# Just return the static page index.html
@app.route('/')
def index():
    return render_template('index.html')

# Creates a new ToDo list. If password is sent, it sets the password for the
# list. Same for the title.
@app.route('/create', methods=['POST'])
def create():
    with connection as c:
        title = request.form['title']
        hashed_password = ''
        if len(request.form['password']) > 0:
            hashed_password = security.get_hash(request.form['password'])
        list_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(5))
        c.execute('INSERT INTO todos (list_id, title, password) VALUES (?, ?, ?)', (list_id, title, hashed_password,))
    return redirect(url_for('todo', list_id=list_id))

# Returns the view for the list with list_id. TODO: If a password is set for that
# list, it should not show the items until logged in.
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
                        'logged': 'password' in request.cookies,
                        'has_password': len(list_data[1]) > 0,
                        'password': list_data[1],
                        'todo': [{'todo':t[0], 'done':t[1], 'item_id':t[2]} for t in todo],
                        'list_id': list_id
                        }
    return render_template('todo.html', **data)

# Adds the item into the list list_id.
@app.route('/add/<list_id>', methods=['POST'])
def add_item(list_id):
    text = request.form['todo']
    with connection as c:
        c.execute('INSERT INTO items (list_id, todo, done) VALUES (?, ?, 0)', (list_id, text,))
    return redirect(url_for('todo', list_id=list_id))

# Removes the item from the list list_id.
@app.route('/remove/<item_id>', methods=['GET'])
def remove(item_id):
    with connection as c:
        c.execute('SELECT list_id FROM items WHERE item_id=?', (item_id,))
        list_id = c.fetchone()[0]
        c.execute('DELETE FROM items WHERE item_id=?', (item_id,))
    return redirect(url_for('todo', list_id=list_id))

# Removes all marked items from the list list_id.
@app.route('/remove_marked/<list_id>', methods=['GET'])
def remove_marked(list_id):
    with connection as c:
        c.execute('DELETE FROM items WHERE list_id=? AND done=1', (list_id,))
    return redirect(url_for('todo', list_id=list_id))

# Marks the item item_id.
@app.route('/mark/<item_id>', methods=['POST'])
def mark(item_id):
    with connection as c:
        c.execute('UPDATE items SET done=1 WHERE item_id=?', (item_id,))
    return 'marked'

# Unmarks the item item_id.
@app.route('/unmark/<item_id>', methods=['POST'])
def unmark(item_id):
    with connection as c:
        c.execute('UPDATE items SET done=0 WHERE item_id=?', (item_id,))
    return 'unmarked'

# Sets the title to the list list_id.
@app.route('/settitle/<list_id>', methods=['POST'])
def set_title(list_id):
    title = request.form['title']
    with connection as c:
        c.execute('UPDATE todos SET title=? WHERE list_id=?', (title, list_id,))
    return redirect(url_for('todo', list_id=list_id))

# Sets the password to the list list_id.
@app.route('/setpassword/<list_id>', methods=['POST'])
def set_password(list_id):
    raw_password = request.form['password']
    response = make_response(redirect(url_for('todo', list_id=list_id)))
    if raw_password:
        hashed_password = security.get_hash(raw_password)
        with connection as c:
            c.execute('UPDATE todos SET password=? WHERE list_id=?', (hashed_password, list_id,))
        response.set_cookie('password', hashed_password)
    return response

# Logs in the user so he can edit a todo list with password.
@app.route('/login/<list_id>', methods=['POST'])
def login(list_id):
    raw_password = request.form['password']
    with connection as c:
        c.execute('SELECT password FROM todos WHERE list_id=?', (list_id,))
        db_password = c.fetchone()[0]
    if security.verify_password(raw_password, db_password):
        response = make_response(redirect(url_for('todo', list_id=list_id)))
        response.set_cookie('password', db_password)
    else:
        response = make_response(redirect(url_for('todo', list_id=list_id)))
    return response

# Logs out the current session
@app.route('/logout/<list_id>', methods=['POST'])
def logout(list_id):
    response = make_response(redirect(url_for('todo', list_id=list_id)))
    response.set_cookie('password', '', expires=0)
    return response
