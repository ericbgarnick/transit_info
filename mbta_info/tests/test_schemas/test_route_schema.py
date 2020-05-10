import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def route_data(agency: mbta_models.Agency, line: mbta_models.Line) -> typing.Dict:
    return {
        "route_id": "Test Route",
        "agency_id": f"{agency.agency_id}",
        "route_short_name": "Test Route",
        "route_long_name": "Test Route Name",
        "route_desc": "Rail Replacement Bus",
        "route_type": "0",
        "route_url": "http://www.route.com",
        "route_color": "FFFFFF",
        "route_text_color": "BBBBBB",
        "route_sort_order": "25",
        "route_fare_class": "Rapid Transit",
        "line_id": f"{line.line_id}",
        "listed_route": ""
    }


def test_load_good_data(route_data: typing.Dict):
    # GIVEN
    route_obj = schemas.RouteSchema().load(route_data)

    # THEN
    assert isinstance(route_obj, mbta_models.Route)
    for key, value in route_data.items():
        if key == "route_type":
            value = getattr(mbta_models.RouteType, value)
        elif key in {"route_sort_order", "agency_id"}:
            value = int(value)
        elif key == "route_fare_class":
            value = getattr(mbta_models.FareClass, value.replace(" ", "_").lower())
        elif key == "route_desc":
            value = getattr(mbta_models.RouteDescription, value.replace(" ", "_").lower())
        elif key == "listed_route":
            value = 0
        assert getattr(route_obj, key) == value


@pytest.mark.parametrize(
    "route_data_update",
    (
        {"route_id": ""},
        {"agency_id": "NAN"},
        {"route_long_name": ""},
        {"route_desc": "Invalid Route Description"},
        {"route_type": "NAN"},
        {"route_url": "bad url"},
        {"route_sort_order": "NAN"},
        {"route_fare_class": "Bad Fare Class"},
        {"line_id": "Bad Line Id"},
        {"listed_route": "2"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(route_data_update: typing.Dict, route_data: typing.Dict):
    # GIVEN
    route_data.update(route_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.RouteSchema().load(route_data)
