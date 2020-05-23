import marshmallow as mm
import pytest
import typing

from flaskr import schemas, models as mbta_models


@pytest.fixture
def route_pattern_data(route: mbta_models.Route) -> typing.Dict:
    return {
        "route_pattern_id": "RoutePattern1",
        "route_id": f"{route.route_id}",
        "direction_id": "1",
        "route_pattern_name": "Test RoutePattern",
        "route_pattern_time_desc": "All the time!",
        "route_pattern_typicality": "3",
        "route_pattern_sort_order": "45",
    }


def test_load_good_data(route_pattern_data: typing.Dict):
    # GIVEN
    route_pattern_obj = schemas.RoutePatternSchema().load(route_pattern_data)

    # THEN
    assert isinstance(route_pattern_obj, mbta_models.RoutePattern)
    for key, value in route_pattern_data.items():
        if key in ["direction_id", "route_pattern_sort_order"]:
            value = int(value)
        elif key == "route_pattern_typicality":
            value = getattr(mbta_models.RoutePatternTypicality, value)
        assert getattr(route_pattern_obj, key) == value


@pytest.mark.parametrize(
    "route_pattern_data_update",
    (
        {"route_pattern_id": ""},
        {"route_id": "bad route id"},
        {"direction_id": "-1"},
        {"route_pattern_typicality": "300"},
        {"route_pattern_sort_order": "NAN"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(
    route_pattern_data_update: typing.Dict, route_pattern_data: typing.Dict
):
    # GIVEN
    route_pattern_data.update(route_pattern_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.RoutePatternSchema().load(route_pattern_data)
