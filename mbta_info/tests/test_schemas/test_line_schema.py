import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def line_data() -> typing.Dict:
    return {
        "line_id": "Test Line",
        "line_short_name": "Test Line",
        "line_long_name": "Test Line Name",
        "line_desc": "Test line description",
        "line_url": "http://www.line.com",
        "line_color": "AAAAAA",
        "line_text_color": "FFFFFF",
        "line_sort_order": "100",
    }


def test_load_good_data(line_data: typing.Dict):
    # GIVEN
    line_obj = schemas.LineSchema().load(line_data)

    # THEN
    assert isinstance(line_obj, mbta_models.Line)
    for key, value in line_data.items():
        if key == "line_sort_order":
            value = int(value)
        assert getattr(line_obj, key) == value


@pytest.mark.parametrize(
    "line_data_update",
    (
        {"line_id": ""},
        {"line_long_name": ""},
        {"line_url": "bad_url"},
        {"line_sort_order": "NAN"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(line_data_update: typing.Dict, line_data: typing.Dict):
    # GIVEN
    line_data.update(line_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.LineSchema().load(line_data)
