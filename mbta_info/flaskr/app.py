import confuse
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

config = confuse.Configuration("transit_info", __name__)

app = Flask(__name__)
for key, value in config["flask"].get().items():
    app.config[key] = value

db = SQLAlchemy(app)
migrate = Migrate(app, db)
