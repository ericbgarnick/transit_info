import marshmallow as mm
import pytest

from mbta_info.flaskr.fields import foreign_key as fk_fields
from mbta_info.tests import models as test_models


def test_deserialize_success(test_model: test_models.TestModel):
    # GIVEN: StringForeignKey field initialized for TestModel
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)

    # THEN: value is returned unchanged without error
    assert string_fk_field.deserialize(test_model.test_id) == test_model.test_id


def test_deserialize_bad_instance_id(test_model: test_models.TestModel):
    # GIVEN: a TestModel instance exists and a StringForeignKey initialized for TestModel
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)

    # THEN: deserializing a test_id value that doesn't exist in the db raises a ValidationError
    with pytest.raises(mm.ValidationError) as excinfo:
        string_fk_field.deserialize("Bad Instance Id")
    assert string_fk_field.is_missing_instance_error(excinfo.value)


def test_deserialize_no_data(db):
    # GIVEN
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)

    # THEN
    with pytest.raises(mm.ValidationError) as excinfo:
        string_fk_field.deserialize("Any Id")
    assert string_fk_field.is_empty_table_error(excinfo.value)


def test_is_empty_table_error_true():
    # GIVEN
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)
    missing_route_error = string_fk_field.make_error(
        "no_model_data", model_name="TestModel"
    )

    # THEN
    assert string_fk_field.is_empty_table_error(missing_route_error) is True


def test_is_missing_instance_error_true():
    # GIVEN
    model_id = "Test1"
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)
    missing_route_error = string_fk_field.make_error(
        "missing_entry", model_name="TestModel", model_id=model_id
    )

    # THEN
    assert string_fk_field.is_missing_instance_error(missing_route_error) is True


@pytest.mark.parametrize(
    "error_check_function_name", ("is_empty_table_error", "is_missing_instance_error")
)
def test_is_x_error_false(error_check_function_name: str):
    # GIVEN
    string_fk_field = fk_fields.StringForeignKey(test_models.TestModel)
    other_validation_error = mm.ValidationError("Dummy message")

    # THEN
    error_check_function = getattr(string_fk_field, error_check_function_name)
    assert error_check_function(other_validation_error) is False
