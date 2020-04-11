import csv
import glob
import inspect
import os

from marshmallow import Schema

import models
import schemas
from db import db

MODEL_NAMES = [m[0].lower() for m in inspect.getmembers(models, inspect.isclass) if m[1].__module__ == models.__name__]

DATA_FILES = ['agency.csv', 'lines.csv', 'routes.csv']


def load_data():
    for data_file_name in DATA_FILES:
        path, file_name = os.path.split(data_file_path)
        model_name = os.path.splitext(file_name)[0].rstrip('s')  # data file name may be pluralized
        model_schema = getattr(schemas, model_name.title() + 'Schema')()  # type: Schema
        with open(data_file_path, 'r') as f_in:
            reader = csv.DictReader(f_in)
            for data_row in reader:
                new_object = model_schema.load(data_row)
                db.session.add(new_object)
    db.session.commit()
    db.session.close()
