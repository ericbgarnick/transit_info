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
DATA_FILES = ['stop_times.csv']


class Loader:
    PROJECT_PATH = Path('mbta_info', 'flaskr', 'data')

    def __init__(self, max_batch_size: int = 100000):
        self._max_batch_size = max_batch_size
        self._parent_dir = Path(__name__).absolute().parent

    def load_data(self):
        for data_file_name in DATA_FILES:
            data_file_path = Path(self._parent_dir.absolute(), Loader.PROJECT_PATH, data_file_name)
            model_name = create_model_name(data_file_name)
            model_schema = getattr(schemas, model_name + 'Schema')()  # type: Schema
            with open(data_file_path, 'r') as f_in:
                reader = csv.DictReader(f_in)
                cur_batch_size = 0
                for data_row in reader:
                    try:
                        new_object = model_schema.load(data_row)
                        db.session.add(new_object)
                        cur_batch_size += 1
                    except (ValidationError, KeyError) as e:
                        print(data_row)
                        raise e
                    if cur_batch_size == self._max_batch_size:
                        try:
                            db.session.commit()
                            print(f"Loaded {cur_batch_size} rows from {data_file_name}")
                            cur_batch_size = 0
                        except DataError as e:
                            db.session.rollback()
                            db.session.close()
                            raise e
                # Commit last batch
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
