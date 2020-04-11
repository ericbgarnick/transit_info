import csv

from marshmallow import Schema
from sqlalchemy.orm import Session


class Loader:
    """
    A class to load data from a csv file, create db models and commit the to the db
    """
    def __init__(self, db_session: Session):
        self.session = db_session

    def load_data(self, data_file_path: str, model_schema: Schema):
        """Read data from input data file and create db entries for data read"""
        with open(data_file_path, 'r') as data_in:
            for entry in csv.DictReader(data_in):
                new_instance = model_schema.load(entry)
                self.session.add(new_instance)
        self.session.commit()
        self.session.close()
