import os
from flask import Flask

app = Flask(__name__)
DATABASE = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'database'
		)

from . import views
