import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def direction_data(route: mbta_models.Route) -> typing.Dict:
    return {
        "route_id": f"{route.route_id}",
        "direction_id": "1",
        "direction": "North",
        "direction_destination": "The end of the world",
    }


def test_load_good_data(direction_data: typing.Dict):
    # GIVEN
    direction_obj = schemas.DirectionSchema().load(direction_data)

    # THEN
    assert isinstance(direction_obj, mbta_models.Direction)
    for key, value in direction_data.items():
        if key == "direction_id":
            value = int(value)
        assert getattr(direction_obj, key) == value


def test_load_data_missing_route(direction_data: typing.Dict):
    """If no Route is found for the given route_id, just skip this Direction data"""
    # GIVEN
    direction_data["route_id"] = "bad route id"
    assert schemas.DirectionSchema().load(direction_data) is None


@pytest.mark.parametrize(
    "direction_data_update",
    (
        {"direction_id": "NAN"},
        {"direction": ""},
        {"direction_destination": ""},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(direction_data_update: typing.Dict, direction_data: typing.Dict):
    # GIVEN
    direction_data.update(direction_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.DirectionSchema().load(direction_data)
