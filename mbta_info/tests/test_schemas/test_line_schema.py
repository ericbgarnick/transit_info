import marshmallow as mm
import pytest

from mbta_info.flaskr import schemas, models as mbta_models


def test_load_good_data():
    # GIVEN
    line_data = {
        "line_id": "Test Line",
        "line_short_name": "Test Line",
        "line_long_name": "Test Line Name",
        "line_desc": "Test line description",
        "line_url": "http://www.line.com",
        "line_color": "AAAAAA",
        "line_text_color": "FFFFFF",
        "line_sort_order": 100,
    }

    # WHEN
    line_obj = schemas.LineSchema().load(line_data)

    # THEN
    assert isinstance(line_obj, mbta_models.Line)
    for key, value in line_data.items():
        assert getattr(line_obj, key) == value


@pytest.mark.parametrize(
    "line_data_update",
    (
        {"line_id": None},
        {"line_long_name": None},
        {"line_url": "bad_url"},
        {"line_sort_order": "NAN"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(line_data_update):
    # GIVEN
    line_data = {
        "line_id": "Test Line",
        "line_short_name": "Test Line",
        "line_long_name": "Test Line Name",
        "line_desc": "Test line description",
        "line_url": "http://www.line.com",
        "line_color": "AAAAAA",
        "line_text_color": "FFFFFF",
        "line_sort_order": 100,
    }
    line_data.update(line_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.LineSchema().load(line_data)
