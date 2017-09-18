from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from app.configurations import config


# initialize sql-alchemy

db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)

    from app.main import api
    app.register_blueprint(api, url_prefix='/api/1_0')

    return app
