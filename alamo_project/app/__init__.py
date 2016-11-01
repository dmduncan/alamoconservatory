from flask import Flask
from flask.ext.login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('config')

mongo = PyMongo(app)

lm = LoginManager()
lm.init_app(app)

from app import views
