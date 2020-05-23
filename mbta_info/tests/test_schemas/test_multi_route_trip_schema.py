import marshmallow as mm
import pytest
import typing

from flaskr import schemas, models as mbta_models


@pytest.fixture
def multi_route_trip_data(route: mbta_models.Route, trip: mbta_models.Trip) -> typing.Dict:
    return {
        "added_route_id": f"{route.route_id}",
        "trip_id": f"{trip.trip_id}",
    }


def test_load_good_data(multi_route_trip_data: typing.Dict):
    # GIVEN
    multi_route_trip_obj = schemas.MultiRouteTripSchema().load(multi_route_trip_data)

    # THEN
    assert isinstance(multi_route_trip_obj, mbta_models.MultiRouteTrip)
    for key, value in multi_route_trip_data.items():
        assert getattr(multi_route_trip_obj, key) == value


@pytest.mark.parametrize(
    "multi_route_trip_data_update",
    (
        {"added_route_id": "bad route id"},
        {"trip_id": ""},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(multi_route_trip_data_update: typing.Dict, multi_route_trip_data: typing.Dict):
    # GIVEN
    multi_route_trip_data.update(multi_route_trip_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.MultiRouteTripSchema().load(multi_route_trip_data)
