import confuse
from flask import Flask

config = confuse.Configuration("transit_info", __name__)


def create_app(env_name: str = "dev"):
    app = Flask(__name__)
    app.config.from_mapping(config["flask"][env_name].get())
    register_extensions(app, env_name == "test")
    return app


def register_extensions(app: Flask, testing):
    from mbta_info.flaskr.database import db
    from mbta_info.flaskr import models as mbta_models

    if testing:
        from mbta_info.tests import models as test_models
    db.init_app(app)
