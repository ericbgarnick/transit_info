import csv
from pathlib import Path
from typing import Dict, Set, Union, List

from flask_sqlalchemy import SQLAlchemy, Model
from marshmallow import Schema, ValidationError
from sqlalchemy import inspect
from sqlalchemy.exc import DataError

from mbta_info.flaskr import schemas, models, app
from mbta_info.flaskr.tools.utils import create_model_name

DATA_FILES = app.config["mbta_data"]["files"].get()
DATA_PATH = Path(
    Path(__name__).absolute().parent, app.config["mbta_data"]["path"].get()
)


class Loader:
    def __init__(self, db: SQLAlchemy, max_batch_size: int = 100000):
        self.db = db
        db.create_all()
        self._max_batch_size = max_batch_size

    def load_data(self, data_files: List[str] = DATA_FILES):
        import pdb

        pdb.set_trace()
        for data_file_name in data_files:
            print(f"Loading data from {data_file_name}")

            model_name = create_model_name(data_file_name)
            model_schema = getattr(schemas, model_name + "Schema")()  # type: Schema
            model = getattr(models, model_name)

            model_pk_field = inspect(model).primary_key[0].name
            existing_pks = {
                tup[0]
                for tup in self.db.session.query(getattr(model, model_pk_field)).all()
            }

            data_file_path = Path(DATA_PATH, data_file_name)
            with open(data_file_path, "r") as f_in:
                reader = csv.DictReader(f_in)
                cur_batch_size = 0
                for data_row in reader:
                    cur_batch_size += self._update_or_create_object(
                        model, model_schema, model_pk_field, existing_pks, data_row
                    )
                    if cur_batch_size == self._max_batch_size:
                        self._commit_batch()
                        print(f"Loaded {cur_batch_size} rows from {data_file_name}")
                        cur_batch_size = 0
                # Commit last batch
                self._commit_batch(last_batch=True)

    def _update_or_create_object(
        self,
        model: Model,
        model_schema: Schema,
        model_pk_field: str,
        existing_pks: Set[Union[str, int]],
        data_row: Dict,
    ) -> int:
        """Update or create a database entry, returning 1 for if
        the data_row was successfully processed, 0 if skipped"""
        try:
            model_instance = model_schema.load(data_row)
            if model_instance:
                instance_pk = getattr(model_instance, model_pk_field)
                if instance_pk in existing_pks:
                    # Update existing
                    instance_dict = (
                        model_instance.__dict__
                    )  # Some values must be converted from data_row format
                    instance_dict.pop("_sa_instance_state", None)
                    self.db.session.query(model).filter(
                        getattr(model, model_pk_field) == instance_pk
                    ).update(instance_dict)
                else:
                    # Create new
                    self.db.session.add(model_instance)
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
