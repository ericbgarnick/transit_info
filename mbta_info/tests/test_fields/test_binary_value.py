import marshmallow as mm
import pytest

from flaskr.fields import binary_value as bv


@pytest.mark.parametrize("value", (1, 0, "1", "0", True, False))
def test_deserialize_success(value):
    # GIVEN
    bin_val_field = bv.BinaryValue()

    # THEN: value is returned unchanged without error
    assert bin_val_field.deserialize(value) == int(value)


@pytest.mark.parametrize("value", (1.1, 0.4, "11", "", set(), [1], 2, -1))
def test_deserialize_failure(value):
    # GIVEN
    bin_val_field = bv.BinaryValue()

    # THEN: ValidationError is raised
    with pytest.raises(mm.ValidationError):
        bin_val_field.deserialize(value)
