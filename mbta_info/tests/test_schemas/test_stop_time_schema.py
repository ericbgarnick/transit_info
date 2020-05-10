import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def stop_time_data(
    trip: mbta_models.Trip, stop: mbta_models.Stop, checkpoint: mbta_models.Checkpoint
) -> typing.Dict:
    return {
        "trip_id": f"{trip.trip_id}",
        "arrival_time": "02:00:00",
        "departure_time": "02:05:00",
        "stop_id": f"{stop.stop_id}",
        "stop_sequence": "214",
        "stop_headsign": "Test Stop",
        "pickup_type": "0",
        "drop_off_type": "0",
        "shape_dist_traveled": "200.23",
        "timepoint": "1",
        "checkpoint_id": f"{checkpoint.checkpoint_id}",
    }


def test_load_good_data(stop_time_data: typing.Dict):
    # GIVEN
    stop_time_obj = schemas.StopTimeSchema().load(stop_time_data)

    # THEN
    assert isinstance(stop_time_obj, mbta_models.StopTime)
    for key, value in stop_time_data.items():
        if key in {"stop_sequence", "timepoint"}:
            value = int(value)
        elif key in {"pickup_type", "drop_off_type"}:
            value = getattr(mbta_models.PickupDropOffType, value)
        elif key == "shape_dist_traveled":
            value = float(value)
        assert getattr(stop_time_obj, key) == value


@pytest.mark.parametrize(
    "stop_time_data_update",
    (
        {"trip_id": "bad trip id"},
        {"arrival_time": "NAN"},
        {"departure_time": "NAN"},
        {"stop_id": "bad stop id"},
        {"stop_sequence": "15.5"},
        {"pickup_type": "10"},
        {"drop_off_type": "NAN"},
        {"shape_dist_traveled": "NAN"},
        {"timepoint": "3"},
        {"checkpoint_id": "bad checkpoint id"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(stop_time_data_update: typing.Dict, stop_time_data: typing.Dict):
    # GIVEN
    stop_time_data.update(stop_time_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.StopTimeSchema().load(stop_time_data)
