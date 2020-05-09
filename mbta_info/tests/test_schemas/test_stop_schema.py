import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, schema_utils, models as mbta_models


@pytest.fixture
def stop_data(stop: mbta_models.Stop) -> typing.Dict:
    return {
        "stop_id": "Stop2",
        "stop_code": "Stop Code",
        "stop_name": "Test Stop",
        "tts_stop_name": "Test Stop",
        "stop_desc": "A Stop for Testing",
        "platform_code": "Platform1",
        "platform_name": "Platform Name",
        "stop_lat": "10.1",
        "stop_lon": "200.23",
        "zone_id": "Zone1",
        "stop_address": "123 Test Street, City, AA, 12345",
        "stop_url": "http://www.stop.com",
        "level_id": "Level1",
        "location_type": "0",
        "parent_station": f"{stop.stop_id}",
        "wheelchair_boarding": "0",
        "municipality": "Muni",
        "on_street": "Test Street",
        "at_street": "Test Avenue",
        "vehicle_type": "0",
        "stop_timezone": "America/New_York",
    }


def test_load_good_data(stop_data: typing.Dict):
    # GIVEN
    stop_obj = schemas.StopSchema().load(stop_data)

    # THEN
    assert isinstance(stop_obj, mbta_models.Stop)
    for key, value in stop_data.items():
        if key == "stop_lat":
            key = "latitude"
            value = float(value)
        elif key in "stop_lon":
            key = "longitude"
            value = float(value)
        elif key == "location_type":
            value = getattr(mbta_models.LocationType, value)
        elif key == "wheelchair_boarding":
            value = getattr(mbta_models.AccessibilityType, value)
        elif key == "vehicle_type":
            value = getattr(mbta_models.RouteType, value)
        elif key == "stop_timezone":
            value = getattr(mbta_models.TimeZone, schema_utils.timezone_enum_key(value))
        assert getattr(stop_obj, key) == value


@pytest.mark.parametrize(
    "stop_data_update",
    (
        {"route_id": ""},
        {"agency_id": "NAN"},
        {"route_long_name": ""},
        {"route_type": "NAN"},
        {"route_url": "bad url"},
        {"route_sort_order": "NAN"},
        {"route_fare_class": "Bad Fare Class"},
        {"line_id": "Bad Line Id"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(stop_data_update, stop_data):
    # GIVEN
    stop_data.update(stop_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.StopSchema().load(stop_data)


