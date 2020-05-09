import marshmallow as mm
import pytest

from mbta_info.flaskr import fields
from mbta_info.tests import models as test_models


def test_deserialize_success(test_model: test_models.TestModel):
    # GIVEN: StringForeignKey field initialized for TestModel
    string_fk_field = fields.StringForeignKey(test_models.TestModel)

    # THEN: value is returned unchanged without error
    assert string_fk_field.deserialize(test_model.test_id) == test_model.test_id


def test_deserialize_bad_instance_id(test_model: test_models.TestModel):
    # GIVEN: a TestModel instance exists and a StringForeignKey initialized for TestModel
    string_fk_field = fields.StringForeignKey(test_models.TestModel)

    # THEN: deserializing a test_id value that doesn't exist in the db raises a ValidationError
    with pytest.raises(mm.ValidationError) as excinfo:
        string_fk_field.deserialize("Bad Instance Id")
    assert fields.StringForeignKey.is_missing_instance_error(excinfo.value)


def test_deserialize_no_routes(db):
    # GIVEN
    route_id_field = fields.StringForeignKey()

    # THEN
    with pytest.raises(mm.ValidationError) as excinfo:
        route_id_field.deserialize("Route Id")
    assert str(excinfo.value) == route_id_field.error_messages["no_routes"]


def test_is_missing_route_error_true():
    # GIVEN
    route_id = "Test Route"
    route_id_field = fields.StringForeignKey()
    missing_route_error = route_id_field.make_error("missing_route", route_id=route_id)

    # THEN
    assert route_id_field.is_missing_instance_error(missing_route_error) is True


def test_is_missing_route_error_false():
    # GIVEN
    other_validation_error = mm.ValidationError("Dummy message")

    # THEN
    assert fields.StringForeignKey.is_missing_instance_error(other_validation_error) is False
