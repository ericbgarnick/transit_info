from typing import Optional

import pytest

from mbta_info.flaskr.schema_utils import timezone_enum_key, numbered_type_enum_key, time_as_seconds


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, None), ("", ""), ("a", "a"), ("/", "_"), ("a/a", "a_a")],
)
def test_timezone_enum_key(raw_value: Optional[str], updated_value: Optional[str]):
    assert timezone_enum_key(raw_value) == updated_value


@pytest.mark.parametrize(
    "raw_value",
    ("a", "1.1", "-1")
)
def test_numbered_type_enum_key_bad_value(raw_value):
    with pytest.raises(TypeError):
        numbered_type_enum_key(raw_value)


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, None), ("", None), ("0", "type_0"), ("234", "type_234")],
)
def test_numbered_type_enum_key_no_default(raw_value: Optional[str], updated_value: Optional[str]):
    assert numbered_type_enum_key(raw_value) == updated_value


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, "type_0"), ("", "type_0"), ("0", "type_0"), ("234", "type_234")],
)
def test_numbered_type_enum_key_with_default(raw_value: Optional[str], updated_value: str):
    assert numbered_type_enum_key(raw_value, default_0=True) == updated_value


@pytest.mark.parametrize(
    "time_string",
    ["", "10-10-10", "10:10", "a:b:c", "abc123"]
)
def test_time_as_seconds_bad_value(time_string: str):
    with pytest.raises(ValueError):
        time_as_seconds(time_string)


@pytest.mark.parametrize(
    "time_string,num_seconds",
    [("00:00:00", 0), ("00:00:10", 10), ("00:10:10", 610), ("10:10:10", 36610)]
)
def test_time_as_seconds(time_string: str, num_seconds: int):
    assert time_as_seconds(time_string) == num_seconds
