import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, models as mbta_models


@pytest.fixture
def checkpoint_data() -> typing.Dict:
    return {
        "checkpoint_id": "Checkpoint1",
        "checkpoint_name": "Test Checkpoint",
    }


def test_load_good_data(checkpoint_data: typing.Dict):
    # GIVEN
    checkpoint_obj = schemas.CheckpointSchema().load(checkpoint_data)

    # THEN
    assert isinstance(checkpoint_obj, mbta_models.Checkpoint)
    for key, value in checkpoint_data.items():
        assert getattr(checkpoint_obj, key) == value


@pytest.mark.parametrize(
    "checkpoint_data_update",
    ({"checkpoint_id": ""}, {"checkpoint_name": ""}, {"bad_key": "anything"},),
)
def test_load_bad_data(
    checkpoint_data_update: typing.Dict, checkpoint_data: typing.Dict
):
    # GIVEN
    checkpoint_data.update(checkpoint_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.CheckpointSchema().load(checkpoint_data)
