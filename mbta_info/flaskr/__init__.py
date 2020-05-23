from flask import Flask, g

from config import Config


def create_app():
    app = Flask(__name__)
    c = Config()
    app.config.from_mapping(c.config["flask"])
    register_extensions(app, c.flask_env == "testing")
    return app


def register_extensions(app: Flask, testing: bool):
    from flaskr.database import db
    from flaskr import models as mbta_models

    if testing:
        from tests import models as test_models
    db.init_app(app)


def set_g():
    c = Config()
    g.config = c.config
    g.env = c.flask_env
