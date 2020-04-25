import csv
import os
from pathlib import Path
from typing import Dict

from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, ValidationError
from sqlalchemy.exc import DataError

from mbta_info.flaskr import schemas

DATA_FILES = [
    'agency.csv',
    'lines.csv',
    'routes.csv',
    'stops.csv',
    'calendar.csv',
    'shapes.csv',
    'route_patterns.csv',
    'trips.csv',
    'checkpoints.csv',
    'stop_times.csv',
    'directions.csv'
]


class Loader:
    PROJECT_PATH = Path('mbta_info', 'flaskr', 'data')

    def __init__(self, db: SQLAlchemy, max_batch_size: int = 100000):
        self.db = db
        db.create_all()
        self._max_batch_size = max_batch_size
        self._parent_dir = Path(__name__).absolute().parent

    def load_data(self):
        for data_file_name in DATA_FILES:
            print(f"Loading data from {data_file_name}")
            data_file_path = Path(self._parent_dir.absolute(), Loader.PROJECT_PATH, data_file_name)
            model_name = create_model_name(data_file_name)
            model_schema = getattr(schemas, model_name + 'Schema')()  # type: Schema
            with open(data_file_path, 'r') as f_in:
                reader = csv.DictReader(f_in)
                cur_batch_size = 0
                for data_row in reader:
                    cur_batch_size += self._update_or_create_object(model_schema, data_row)
                    if cur_batch_size == self._max_batch_size:
                        self._commit_batch()
                        print(f"Loaded {cur_batch_size} rows from {data_file_name}")
                        cur_batch_size = 0
                # Commit last batch
                self._commit_batch(last_batch=True)

    def _update_or_create_object(self, model_schema: Schema, data_row: Dict) -> int:
        try:
            new_object = model_schema.load(data_row)
            if new_object:
                self.db.session.add(new_object)
                return 1
            return 0
        except (ValidationError, KeyError) as e:
            print(data_row)
            raise e

    def _commit_batch(self, last_batch: bool = False):
        try:
            self.db.session.commit()
            if last_batch:
                self.db.session.close()
        except DataError as e:
            print(e)
            self.db.session.rollback()
            self.db.session.close()
            raise e


def create_model_name(data_file_name: str) -> str:
    raw_file_name = os.path.splitext(data_file_name)[0]
    words_no_plural = raw_file_name.rstrip('s').split('_')
    return ''.join([word.title() for word in words_no_plural])
