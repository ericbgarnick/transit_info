import marshmallow as mm
import pytest
import typing

from flaskr import schemas, models as mbta_models


@pytest.fixture
def shape_data() -> typing.Dict:
    return {
        "shape_id": "shape1",
        "shape_pt_lat": "12.345",
        "shape_pt_lon": "23.456",
        "shape_pt_sequence": "155",
        "shape_dist_traveled": "99.98",
    }


def test_load_good_data(shape_data: typing.Dict):
    # GIVEN
    shape_obj = schemas.ShapeSchema().load(shape_data)

    # THEN
    assert isinstance(shape_obj, mbta_models.Shape)
    for key, value in shape_data.items():
        if key in ["shape_pt_lat", "shape_pt_lon", "shape_dist_traveled"]:
            value = float(value)
        if key == "shape_pt_lat":
            key = "latitude"
        elif key == "shape_pt_lon":
            key = "longitude"
        elif key == "shape_pt_sequence":
            value = int(value)
        assert getattr(shape_obj, key) == value


@pytest.mark.parametrize(
    "shape_data_update",
    (
        {"shape_id": ""},
        {"shape_pt_lat": "NAN"},
        {"shape_pt_lon": ""},
        {"shape_pt_sequence": "1.1"},
        {"shape_dist_traveled": "NAN"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(shape_data_update: typing.Dict, shape_data: typing.Dict):
    # GIVEN
    shape_data.update(shape_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.ShapeSchema().load(shape_data)
