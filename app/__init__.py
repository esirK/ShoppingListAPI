from flask import Flask
from flask_migrate import Migrate

from app.configurations import config

from app.apis.v1 import api, bp, ns
from app.init_db import db

from flask_cors import CORS

api.add_namespace(ns, path="/v1")


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.supports_credentials = True
    Migrate(app, db)
    app.config.from_object(config[config_name])
    app.register_blueprint(bp)
    db.init_app(app)
    return app
