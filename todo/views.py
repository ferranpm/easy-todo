import os
import sqlite3
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
from . import models

# TODO: remove this connection (only use the one in models.py)
connection = utils.Connection(DATABASE)

# Just return the static page index.html
@app.route('/')
def index():
    return render_template('index.html')

# Creates a new ToDo list. If password is sent, it sets the password for the
# list. Same for the title.
@app.route('/create', methods=['POST'])
def create():
    title = request.form['title']
    password = request.form['password']
    li = models.List.create(title, password)
    return redirect(url_for('todo', list_id=li.get_id()))

# Deletes a list
@app.route('/delete/<list_id>', methods=['POST'])
def delete(list_id):
    if utils.has_permission(list_id, request.cookies):
        li = models.List.get_by_id(list_id)
        li.delete()
    return redirect('/')

# Returns the view for the list with list_id.
@app.route('/<list_id>')
def todo(list_id):
    li = models.List.get_by_id(list_id)
    if not li:
        return render_template('notfound.html', list_id=list_id)
    # TODO: Check if logged in
    return render_template('todo.html', li=li)

# Adds the item into the list list_id.
@app.route('/add/<list_id>', methods=['POST'])
def add_item(list_id):
    if utils.has_permission(list_id, request.cookies):
        text = request.form['todo']
        models.Item.new(list_id, text, False)
    return redirect(url_for('todo', list_id=list_id))

# Removes the item from the list list_id.
@app.route('/remove/<list_id>/<item_id>', methods=['GET'])
def remove(list_id, item_id):
    if utils.has_permission(list_id, request.cookies):
        models.Item.remove(list_id, item_id)
    return redirect(url_for('todo', list_id=list_id))

# Removes all marked items from the list list_id.
@app.route('/remove_marked/<list_id>', methods=['GET'])
def remove_marked(list_id):
    if utils.has_permission(list_id, request.cookies):
        li = models.List.get_by_id(list_id)
        li.remove_marked()
    return redirect(url_for('todo', list_id=list_id))

# Marks the item item_id.
@app.route('/mark/<list_id>/<item_id>', methods=['GET'])
def mark(list_id, item_id):
    if utils.has_permission(list_id, request.cookies):
        item = models.Item.get_by_id(list_id, item_id)
        item.mark()
    return redirect(url_for('todo', list_id=list_id))

# Unmarks the item item_id.
@app.route('/unmark/<list_id>/<item_id>', methods=['GET'])
def unmark(list_id, item_id):
    if utils.has_permission(list_id, request.cookies):
        item = models.Item.get_by_id(list_id, item_id)
        item.unmark()
    return redirect(url_for('todo', list_id=list_id))

# Sets the title to the list list_id.
@app.route('/settitle/<list_id>', methods=['POST'])
def set_title(list_id):
    if utils.has_permission(list_id, request.cookies):
        title = request.form['title']
        li = models.List.get_by_id(list_id)
        li.set_title(title)
    return redirect(url_for('todo', list_id=list_id))

# Sets the password to the list list_id.
@app.route('/setpassword/<list_id>', methods=['POST'])
def set_password(list_id):
    raw_password = request.form['password']
    response = make_response(redirect(url_for('todo', list_id=list_id)))
    li = models.List.get_by_id(list_id)
    hashed_password = li.set_password(raw_password)
    if hashed_password:
        response.set_cookie('password', hashed_password)
    return response

# Logs in the user so he can edit a todo list with password.
@app.route('/login/<list_id>', methods=['POST'])
def login(list_id):
    raw_password = request.form['password']
    li = models.List.get_by_id(list_id)
    if utils.verify_password(raw_password, li.get_password()):
        response = make_response(redirect(url_for('todo', list_id=list_id)))
        response.set_cookie('password', li.get_password())
    else:
        response = make_response(redirect(url_for('todo', list_id=list_id)))
    return response

# Logs out the current session
@app.route('/logout/<list_id>', methods=['POST'])
def logout(list_id):
    response = make_response(redirect(url_for('todo', list_id=list_id)))
    response.set_cookie('password', '', expires=0)
    return response
