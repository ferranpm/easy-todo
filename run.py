from todo import utils
from todo import app

if not utils.db_exists():
    utils.db_init()

app.run(debug=True)
