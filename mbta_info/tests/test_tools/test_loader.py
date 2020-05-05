import pathlib
from unittest import mock

import pytest
import typing

from sqlalchemy.exc import DataError

from mbta_info.flaskr.tools.loader import Loader
from mbta_info.tests import models as test_models
from mbta_info.tests import schemas as test_schemas


class TableStub:
    def __init__(self, name: str):
        self.name = name


class DbStub:
    class MetaData:
        def __init__(self, tables: typing.List[TableStub]):
            self.sorted_tables = tables

    def __init__(self, tables: typing.List[TableStub]):
        self.metadata = self.MetaData(tables)


@pytest.mark.parametrize("batch_size_to_set, batch_size_expected", [([], 100000), ([10], 10)])
def test_init(batch_size_to_set, batch_size_expected, db, monkeypatch):
    """Assert Loader calls db.create_all(), sets max_batch_size and table_names"""
    # GIVEN
    monkeypatch.setattr(db, 'create_all', mock.Mock())
    table_names = [
        'agency', 'calendar', 'checkpoint', 'geo_stub', 'line', 'shape', 'stop',
        'route', 'test_model', 'direction', 'route_pattern', 'trip', 'stop_time'
    ]
    loader_args = [db] + batch_size_to_set

    # WHEN
    loader = Loader(*loader_args)

    # THEN
    db.create_all.assert_called_once()
    assert loader.max_batch_size == batch_size_expected
    assert sorted(loader.table_names) == sorted(table_names)


@pytest.mark.parametrize(
    "last_batch, expected_calls",
    [
        (False, ("commit",)),
        (True, ("commit", "close"))
    ]
)
def test_commit_batch_success(last_batch, expected_calls, db, monkeypatch):
    """Assert commit() and close() calls when no data exception occurs"""
    # GIVEN
    monkeypatch.setattr(db.session, "commit", mock.Mock())
    monkeypatch.setattr(db.session, "rollback", mock.Mock())
    monkeypatch.setattr(db.session, "close", mock.Mock())

    # WHEN
    loader = Loader(db)
    loader.commit_batch(last_batch=last_batch)

    # THEN
    for expected_call in expected_calls:
        getattr(db.session, expected_call).assert_called_once()
    db.session.rollback.assert_not_called()


def test_commit_batch_failure(db, monkeypatch):
    """Assert rollback() and close() called and error re-raised when a DataError occurs"""
    # GIVEN
    def raise_data_error():
        raise DataError(None, None, None)
    monkeypatch.setattr(db.session, "commit", mock.Mock(side_effect=raise_data_error))
    monkeypatch.setattr(db.session, "rollback", mock.Mock())
    monkeypatch.setattr(db.session, "close", mock.Mock())

    with pytest.raises(DataError):
        # WHEN
        loader = Loader(db)
        loader.commit_batch()

    # THEN
    db.session.commit.assert_called_once()
    db.session.rollback.assert_called_once()
    db.session.close.assert_called_once()


def test_get_model_for_table(db):
    # GIVEN
    table_name = "test_model"
    expected_model = test_models.TestModel

    # WHEN
    loader = Loader(db)

    # THEN
    assert loader.get_model_for_table(table_name) is expected_model


def test_get_schema_for_table(db):
    # GIVEN
    table_name = "test_model"
    expected_schema = test_schemas.TestModelSchema

    # WHEN
    loader = Loader(db)

    # THEN
    assert isinstance(loader.get_schema_for_table(table_name), expected_schema)


def test_get_data_file_path(db):
    # GIVEN
    table_name = "test_model"
    expected_path = pathlib.Path(pathlib.Path(__name__).cwd(), f"mbta_info/data/{table_name}s.txt")

    # WHEN
    loader = Loader(db)

    # THEN
    assert loader.get_data_file_path(table_name) == expected_path
