import datetime

import marshmallow as mm
import pytest
import typing

from flaskr import schemas, models as mbta_models


@pytest.fixture
def calendar_attribute_data(calendar: mbta_models.Calendar) -> typing.Dict:
    return {
        "service_id": f"{calendar.service_id}",
        "service_description": "Fancy schedule",
        "service_schedule_name": "Fancy",
        "service_schedule_type": "Weekday",
        "service_schedule_typicality": "1",
        "rating_start_date": "20200101",
        "rating_end_date": "20210202",
        "rating_description": "All-year",
    }


def test_load_good_data(calendar_attribute_data: typing.Dict):
    # GIVEN
    calendar_attribute_obj = schemas.CalendarAttributeSchema().load(
        calendar_attribute_data
    )

    # THEN
    assert isinstance(calendar_attribute_obj, mbta_models.CalendarAttribute)
    for key, value in calendar_attribute_data.items():
        if key == "service_schedule_type":
            value = getattr(mbta_models.ServiceScheduleType, value)
        elif key == "service_schedule_typicality":
            value = getattr(mbta_models.ServiceScheduleTypicality, value)
        elif key.endswith("date"):
            value = datetime.datetime.strptime(value, schemas.DATE_INPUT_FORMAT).date()
        assert getattr(calendar_attribute_obj, key) == value


@pytest.mark.parametrize(
    "calendar_attribute_data_update",
    (
        {"service_id": "bad service id"},
        {"service_description": ""},
        {"service_schedule_name": ""},
        {"service_schedule_type": "Birthday"},
        {"service_schedule_typicality": "1000"},
        {"rating_start_date": "2020-01-01"},
        {"rating_end_date": "2021, February 2nd"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(
    calendar_attribute_data_update: typing.Dict, calendar_attribute_data: typing.Dict
):
    # GIVEN
    calendar_attribute_data.update(calendar_attribute_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.CalendarAttributeSchema().load(calendar_attribute_data)
