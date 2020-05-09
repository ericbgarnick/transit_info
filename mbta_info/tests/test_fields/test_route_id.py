import marshmallow as mm
import pytest

from mbta_info.flaskr import fields, models as mbta_models


def test_deserialize_success(db, agency):
    # GIVEN
    route_id = "Test Route"
    route = mbta_models.Route(
        route_id, agency.agency_id, "Test Route Name", mbta_models.RouteType.type_0
    )
    db.session.add(route)
    db.session.commit()
    route_id_field = fields.RouteId()

    # THEN
    assert route_id_field.deserialize(route_id) == route_id


def test_deserialize_bad_route_id(db, agency):
    # GIVEN
    route_id = "Test Route"
    route = mbta_models.Route(
        route_id, agency.agency_id, "Test Route Name", mbta_models.RouteType.type_0
    )
    db.session.add(route)
    db.session.commit()
    route_id_field = fields.RouteId()

    # THEN
    with pytest.raises(mm.ValidationError) as excinfo:
        route_id_field.deserialize("Bad Route Id")
    assert fields.RouteId.is_missing_route_error(excinfo.value)


def test_deserialize_no_routes(db):
    # GIVEN
    route_id_field = fields.RouteId()

    # THEN
    with pytest.raises(mm.ValidationError) as excinfo:
        route_id_field.deserialize("Route Id")
    assert str(excinfo.value) == route_id_field.error_messages["no_routes"]


def test_is_missing_route_error_true():
    # GIVEN
    route_id = "Test Route"
    route_id_field = fields.RouteId()
    missing_route_error = route_id_field.make_error("missing_route", route_id=route_id)

    # THEN
    assert route_id_field.is_missing_route_error(missing_route_error) is True


def test_is_missing_route_error_false():
    # GIVEN
    other_validation_error = mm.ValidationError("Dummy message")

    # THEN
    assert fields.RouteId.is_missing_route_error(other_validation_error) is False
