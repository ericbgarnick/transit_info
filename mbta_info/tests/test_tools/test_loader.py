import json
import pathlib
from unittest import mock

import pytest
import marshmallow as mm

from sqlalchemy.exc import DataError

from flaskr.tools.loader import Loader
from tests import models as test_models
from tests import schemas as test_schemas


@pytest.mark.parametrize(
    "batch_size_to_set, batch_size_expected", [([], 100000), ([10], 10)]
)
def test_init(batch_size_to_set, batch_size_expected, db, monkeypatch):
    """Assert Loader calls db.create_all(), sets max_batch_size and table_names"""
    # GIVEN
    monkeypatch.setattr(db, "create_all", mock.Mock())
    table_names = [  # Order matters for dependencies
        "agency",
        "calendar",
        "calendar_attribute",
        "calendar_date",
        "checkpoint",
        "geo_stub",
        "line",
        "shape",
        "stop",
        "route",
        "test_model",
        "direction",
        "route_pattern",
        "trip",
        "stop_time",
        "linked_dataset",
        "multi_route_trip",
    ]
    loader_args = [db] + batch_size_to_set

    # WHEN
    loader = Loader(*loader_args)

    # THEN
    db.create_all.assert_called_once()
    assert loader.max_batch_size == batch_size_expected
    assert sorted(loader.table_names) == sorted(table_names)


@pytest.mark.parametrize(
    "last_batch, expected_calls", [(False, ("commit",)), (True, ("commit", "close"))]
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
    monkeypatch.setattr(
        db.session, "commit", mock.Mock(side_effect=DataError(None, None, None))
    )
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
    expected_path = pathlib.Path(
        pathlib.Path(__name__).absolute().parent, f"data/{table_name}s.txt"
    )

    # WHEN
    loader = Loader(db)

    # THEN
    assert loader.get_data_file_path(table_name) == expected_path


def test_update_or_create_object_new_obj(db):
    """Assert that given good data, a new object is successfully created"""
    # GIVEN
    geo_stub = test_models.GeoStub(1, 10.1, 20.2)
    db.session.add(geo_stub)
    db.session.commit()

    model = test_models.TestModel
    schema = test_schemas.TestModelSchema()
    model_pk_field = "test_id"
    existing_pks = set()
    data_row = {
        "test_id": "test1",
        "test_name": "test_name",
        "test_type": "0",
        "test_order": 15,
        "test_dist": 0.5,
        "geo_stub_id": geo_stub.geo_stub_id,
    }

    # WHEN
    loader = Loader(db)
    created_objects = loader.update_or_create_object(
        model, schema, model_pk_field, existing_pks, data_row
    )

    # THEN
    assert created_objects == 1

    created_test_model = db.session.query(model).first()  # type: test_models.TestModel
    for key, value in data_row.items():
        if key == "test_type":
            assert created_test_model.test_type == test_models.TestType.type_0
        else:
            assert getattr(created_test_model, key) == value


def test_update_or_create_object_existing_obj(db):
    """Assert that given good data, an existing object is successfully updated"""
    # GIVEN
    geo_stub = test_models.GeoStub(1, 10.1, 20.2)
    existing_test_model = test_models.TestModel(
        "test1", "old_test_name", test_models.TestType.type_0
    )
    db.session.add(geo_stub)
    db.session.add(existing_test_model)
    db.session.commit()

    model = test_models.TestModel
    schema = test_schemas.TestModelSchema()
    model_pk_field = "test_id"
    existing_pks = {
        "test1",
    }
    data_row = {
        "test_id": "test1",
        "test_name": "new_test_name",  # change from "old_test_name"
        "test_type": "1",  # change from type_0
        "test_order": 12,  # Fill blank value
        "test_dist": 0.5,  # Fill blank value
        "geo_stub_id": geo_stub.geo_stub_id,  # Fill blank value
    }

    # WHEN
    loader = Loader(db)
    created_objects = loader.update_or_create_object(
        model, schema, model_pk_field, existing_pks, data_row
    )

    # THEN
    assert created_objects == 0

    created_test_model = db.session.query(model).first()  # type: test_models.TestModel
    for key, value in data_row.items():
        if key == "test_type":
            assert created_test_model.test_type == test_models.TestType.type_1
        else:
            assert getattr(created_test_model, key) == value


def test_update_or_create_object_bad_data(db, capsys):
    """Assert that given bad data, an exception is raised and the received data row is printed"""
    # GIVEN
    model = test_models.TestModel
    schema = test_schemas.TestModelSchema()
    model_pk_field = "test_id"
    existing_pks = set()
    data_row = {
        "test_id": "",
        "test_name": "test_name",
        "test_type": "NAN",
    }

    # WHEN
    loader = Loader(db)
    with pytest.raises(mm.ValidationError):
        loader.update_or_create_object(
            model, schema, model_pk_field, existing_pks, data_row
        )

    # THEN
    assert db.session.query(model).count() == 0
    assert capsys.readouterr().out.strip() == json.dumps(
        data_row, sort_keys=True, indent=4
    )


def test_update_or_create_object_no_object(db, capsys):
    """Test that no exception occurs, but created objects count is
    0 when no object can be created for the given data."""
    # GIVEN
    model = test_models.TestModel
    schema = test_schemas.TestModelSchema()
    model_pk_field = "test_id"
    existing_pks = set()
    data_row = {
        "test_id": "skip_me",
        "test_name": "test_name",
        "test_type": "0",
        "test_order": 15,
        "test_dist": 0.5,
        "geo_stub_id": "does not matter",
    }

    # WHEN
    loader = Loader(db)
    created_objects = loader.update_or_create_object(
        model, schema, model_pk_field, existing_pks, data_row
    )

    # THEN
    assert created_objects == 0
    assert db.session.query(model).count() == 0
    assert not capsys.readouterr().out


def test_load_data_full_run(db, monkeypatch, capsys):
    """Test that data is successfully loaded from files."""
    # GIVEN
    model_names = ["geo_stub", "test_model"]
    test_tables = {k: v for k, v in db.metadata.tables.items() if v.name in model_names}
    monkeypatch.setattr(db.metadata, "tables", test_tables)

    # WHEN
    loader = Loader(db, max_batch_size=2)
    loader.load_data()

    # THEN
    assert db.session.query(test_models.GeoStub).count() == 2
    assert db.session.query(test_models.TestModel).count() == 5
    captured = capsys.readouterr().out.strip()
    for model_name in model_names:
        assert f"Loading data for {model_name} table" in captured
        assert f"transit_info/mbta_info/data/{model_name}s.txt" in captured
