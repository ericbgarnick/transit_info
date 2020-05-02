import flask_sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

db = flask_sqlalchemy.SQLAlchemy()

Base = declarative_base()
