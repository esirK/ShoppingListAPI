from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from app.configurations import config

# initialize sql-alchemy

db = SQLAlchemy()
app = Flask(__name__)
api = Api(app, version='1.0', title='ShoppingList API',
          description='A ShoppingList API For Users To Create, Edit and Share ShoppingLists'
          )


def create_app(config_name):
    from app.main import AddUser
    app.config.from_object(config[config_name])
    db.init_app(app)

    return app
