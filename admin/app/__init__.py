import sys
sys.path.insert(0, 'lib')

from flask import Flask
app = Flask(__name__)
app.config.from_object('config')

from app import views
