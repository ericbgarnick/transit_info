import marshmallow as mm
import pytest

from mbta_info.flaskr import schemas, schema_utils, models as mbta_models


def test_load_good_data(agency, line):
    # GIVEN
    route_data = {
        "route_id": "Test Route",
        "agency_id": f"{agency.agency_id}",
        "route_short_name": "Test Route",
        "route_long_name": "Test Route Name",
        "route_desc": "A Route for Testing",
        "route_type": "0",
        "route_url": "http://www.route.com",
        "route_color": "FFFFFF",
        "route_text_color": "BBBBBB",
        "route_sort_order": "25",
        "route_fare_class": "Rapid Transit",
        "line_id": f"{line.line_id}",
    }

    # WHEN
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
        assert getattr(route_obj, key) == value


@pytest.mark.parametrize(
    "route_data_update",
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
def test_load_bad_data(route_data_update, agency, line):
    # GIVEN
    route_data = {
        "route_id": "Test Route",
        "agency_id": f"{agency.agency_id}",
        "route_short_name": "Test Route",
        "route_long_name": "Test Route Name",
        "route_desc": "A Route for Testing",
        "route_type": "0",
        "route_url": "http://www.route.com",
        "route_color": "FFFFFF",
        "route_text_color": "BBBBBB",
        "route_sort_order": "25",
        "route_fare_class": "Rapid Transit",
        "line_id": f"{line.line_id}",
    }
    route_data.update(route_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.RouteSchema().load(route_data)
