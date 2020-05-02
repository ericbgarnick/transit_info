import confuse
from flask import Flask

config = confuse.Configuration("transit_info", __name__)


def create_app(env_name: str = "dev"):
    app = Flask(__name__)
    app.config.from_mapping(config["flask"][env_name].get())
    register_extensions(app)
    return app


def register_extensions(app: Flask):
    from mbta_info.flaskr.database import db
    db.init_app(app)
