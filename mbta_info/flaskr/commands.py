import csv
import os
from pathlib import Path

from marshmallow import Schema, ValidationError
from sqlalchemy.exc import DataError

from mbta_info.flaskr import schemas
from mbta_info.flaskr.app import db

# DATA_FILES = [
#     'agency.csv',
#     'lines.csv',
#     'routes.csv',
#     'stops.csv',
#     'calendar.csv',
#     'shapes.csv',
#     'route_patterns.csv',
#     'trips.csv',
#     'checkpoints.csv',
#     'stop_times.csv'
# ]
DATA_FILES = ['checkpoints.csv']


def load_data():
    here = Path(__name__).absolute().parent
    for data_file_name in DATA_FILES:
        data_file_path = Path(here.absolute(), 'mbta_info', 'flaskr', 'data', data_file_name)
        model_name = create_model_name(data_file_name)
        model_schema = getattr(schemas, model_name + 'Schema')()  # type: Schema
        with open(data_file_path, 'r') as f_in:
            reader = csv.DictReader(f_in)
            row_count = 0
            for data_row in reader:
                try:
                    new_object = model_schema.load(data_row)
                    db.session.add(new_object)
                    row_count += 1
                except (ValidationError, KeyError) as e:
                    print(data_row)
                    raise e
                if row_count % 10000 == 0:
                    print(f"Loaded {row_count} rows from {data_file_name}")

    try:
        db.session.commit()
    except DataError as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()


def create_model_name(data_file_name: str) -> str:
    raw_file_name = os.path.splitext(data_file_name)[0]
    words_no_plural = raw_file_name.rstrip('s').split('_')
    return ''.join([word.title() for word in words_no_plural])
