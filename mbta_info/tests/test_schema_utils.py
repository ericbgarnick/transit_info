from typing import Optional

import marshmallow as mm
import pytest

from flaskr import schema_utils


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, None), ("", ""), ("a", "a"), ("/", "_"), ("a/a", "a_a")],
)
def test_timezone_enum_key(raw_value: Optional[str], updated_value: Optional[str]):
    assert schema_utils.timezone_enum_key(raw_value) == updated_value


@pytest.mark.parametrize("raw_value", ("a", "1.1", "-1"))
def test_numbered_type_enum_key_bad_value(raw_value):
    with pytest.raises(mm.ValidationError):
        schema_utils.numbered_type_enum_key(raw_value)


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, None), ("", None), ("0", "type_0"), ("234", "type_234")],
)
def test_numbered_type_enum_key_no_default(
    raw_value: Optional[str], updated_value: Optional[str]
):
    assert schema_utils.numbered_type_enum_key(raw_value) == updated_value


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, "type_0"), ("", "type_0"), ("0", "type_0"), ("234", "type_234")],
)
def test_numbered_type_enum_key_with_default(
    raw_value: Optional[str], updated_value: str
):
    assert (
        schema_utils.numbered_type_enum_key(raw_value, default_0=True) == updated_value
    )


@pytest.mark.parametrize("time_string", ["", "10-10-10", "10:10", "a:b:c", "abc123"])
def test_time_as_seconds_bad_value(time_string: str):
    with pytest.raises(mm.ValidationError):
        schema_utils.time_as_seconds(time_string)


@pytest.mark.parametrize(
    "time_string,num_seconds",
    [("00:00:00", 0), ("00:00:10", 10), ("00:10:10", 610), ("10:10:10", 36610)],
)
def test_time_as_seconds(time_string: str, num_seconds: int):
    assert schema_utils.time_as_seconds(time_string) == num_seconds


@pytest.mark.parametrize("input_val, result", [("1", True), ("0", False)])
def test_int_str_to_bool_good_data(input_val: str, result: bool):
    assert schema_utils.int_str_to_bool(input_val) is result


@pytest.mark.parametrize("input_val", ("2", "a", "1.0", "", 1, 0, True, False, 1.0))
def test_int_str_to_bool_bad_data(input_val: str):
    with pytest.raises(mm.ValidationError):
        schema_utils.int_str_to_bool(input_val)
