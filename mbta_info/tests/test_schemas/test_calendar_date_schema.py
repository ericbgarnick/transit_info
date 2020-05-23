import datetime

import marshmallow as mm
import pytest
import typing

from flaskr import schemas, models as mbta_models


@pytest.fixture
def calendar_date_data(calendar: mbta_models.Calendar) -> typing.Dict:
    return {
        "service_id": f"{calendar.service_id}",
        "date": "20200704",
        "exception_type": "1",
        "holiday_name": "US Independence Day",
    }


def test_load_good_data(calendar_date_data: typing.Dict):
    # GIVEN
    calendar_date_obj = schemas.CalendarDateSchema().load(calendar_date_data)

    # THEN
    assert isinstance(calendar_date_obj, mbta_models.CalendarDate)
    for key, value in calendar_date_data.items():
        if key == "exception_type":
            value = getattr(mbta_models.DateExceptionType, value)
        elif key == "date":
            value = datetime.datetime.strptime(value, schemas.DATE_INPUT_FORMAT).date()
        assert getattr(calendar_date_obj, key) == value


@pytest.mark.parametrize(
    "calendar_date_data_update",
    (
        {"service_id": "bad service id"},
        {"date": "2020-01-01"},
        {"exception_type": "0"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(
    calendar_date_data_update: typing.Dict, calendar_date_data: typing.Dict
):
    # GIVEN
    calendar_date_data.update(calendar_date_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.CalendarDateSchema().load(calendar_date_data)
