from flask_sqlalchemy import Model
from sqlalchemy import inspect


def pk_field_name(model: Model) -> str:
    return inspect(model).primary_key[0].name
