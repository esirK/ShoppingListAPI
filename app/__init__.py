from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.configurations import config

# initialize sql-alchemy

db = SQLAlchemy()
from app.apis.v1 import api, bp, ns

api.add_namespace(ns, path="/v_1")


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.register_blueprint(bp)
    db.init_app(app)
    return app
