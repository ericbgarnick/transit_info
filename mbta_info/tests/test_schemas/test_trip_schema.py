import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, schema_utils, models as mbta_models


@pytest.fixture
def trip_data(route: mbta_models.Route, calendar: mbta_models.Calendar, route_pattern: mbta_models.RoutePattern) -> typing.Dict:
    return {
        "route_id": f"{route.route_id}",
        "service_id": f"{calendar.service_id}",
        "trip_id": "trip1",
        "trip_headsign": "Trip 1",
        "trip_short_name": "Test Trip",
        "direction_id": "1",
        "block_id": "block1",
        "shape_id": "shape1",
        "wheelchair_accessible": "1",
        "trip_route_type": "0",
        "route_pattern_id": f"{route_pattern.route_pattern_id}",
        "bikes_allowed": "1",
    }


def test_load_good_data(trip_data: typing.Dict):
    # GIVEN
    trip_obj = schemas.TripSchema().load(trip_data)

    # THEN
    assert isinstance(trip_obj, mbta_models.Trip)
    for key, value in trip_data.items():
        if key == "direction_id":
            value = int(value)
        elif key == "wheelchair_accessible":
            value = getattr(mbta_models.TripAccessibility, value)
        elif key == "trip_route_type":
            value = getattr(mbta_models.RouteType, value)
        elif key == "bikes_allowed":
            value = getattr(mbta_models.TripAccessibility, value)
        assert getattr(trip_obj, key) == value


@pytest.mark.parametrize(
    "trip_data_update",
    (
        {"route_id": "bad route id"},
        {"service_id": "bad service id"},
        {"trip_id": ""},
        {"direction_id": "NAN"},
        {"wheelchair_accessible": "100"},
        {"trip_route_type": "35"},
        {"route_pattern_id": "bad route pattern id"},
        {"bikes_allowed": "NAN"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(trip_data_update: typing.Dict, trip_data: typing.Dict):
    # GIVEN
    trip_data.update(trip_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.TripSchema().load(trip_data)
