import pytest

from mbta_info.flaskr.schema_utils import timezone_enum_key


@pytest.mark.parametrize(
    "raw_value,updated_value",
    [(None, None), ("", ""), ("a", "a"), ("/", "_"), ("a/a", "a_a")],
)
def test_timezone_enum_key(raw_value, updated_value):
    assert timezone_enum_key(raw_value) == updated_value
