import datetime

import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def calendar_data() -> typing.Dict:
    return {
        "service_id": "Service1",
        "monday": "1",
        "tuesday": "0",
        "wednesday": "1",
        "thursday": "0",
        "friday": "1",
        "saturday": "0",
        "sunday": "1",
        "start_date": "20200427",
        "end_date": "20210427",
    }


def test_load_good_data(calendar_data: typing.Dict):
    # GIVEN
    calendar_obj = schemas.CalendarSchema().load(calendar_data)

    # THEN
    assert isinstance(calendar_obj, mbta_models.Calendar)
    for key, value in calendar_data.items():
        if key.endswith("day"):
            value = bool(int(value))
        elif key.endswith("date"):
            value = datetime.datetime.strptime(value, schemas.CalendarSchema.DATE_INPUT_FORMAT).date()
        assert getattr(calendar_obj, key) == value


@pytest.mark.parametrize(
    "calendar_data_update",
    (
        {"service_id": ""},
        {"monday": "NAN"},
        {"tuesday": "5"},
        {"wednesday": ""},
        {"thursday": ""},
        {"friday": ""},
        {"saturday": "1.0"},
        {"sunday": "NAN"},
        {"start_date": "2020-01-01"},
        {"end_date": "bad date"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(calendar_data_update: typing.Dict, calendar_data: typing.Dict):
    # GIVEN
    calendar_data.update(calendar_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.CalendarSchema().load(calendar_data)
