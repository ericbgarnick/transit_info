import marshmallow as mm
import pytest
import typing

from mbta_info.flaskr import schemas, schema_utils, models as mbta_models


@pytest.fixture
def linked_dataset_data() -> typing.Dict:
    return {
        "url": "http://www.linked-data.com",
        "trip_updates": "1",
        "vehicle_positions": "0",
        "service_alerts": "0",
        "authentication_type": "0",
    }


def test_load_good_data(linked_dataset_data):
    # GIVEN
    linked_dataset_obj = schemas.LinkedDatasetSchema().load(linked_dataset_data)

    # THEN
    assert isinstance(linked_dataset_obj, mbta_models.LinkedDataset)
    for key, value in linked_dataset_data.items():
        if key == "authentication_type":
            value = getattr(mbta_models.AuthenticationType, value)
        elif key != "url":
            value = int(value)
        assert getattr(linked_dataset_obj, key) == value


@pytest.mark.parametrize(
    "linked_dataset_data_update",
    (
        {"url": "bad url"},
        {"trip_updates": "NAN"},
        {"vehicle_positions": "NAN"},
        {"service_alerts": ""},
        {"authentication_type": "25"},
        {"bad_key": "anything"},
    ),
)
def test_load_bad_data(
    linked_dataset_data_update: typing.Dict, linked_dataset_data: typing.Dict
):
    # GIVEN
    linked_dataset_data.update(linked_dataset_data_update)

    # THEN
    with pytest.raises(mm.ValidationError):
        schemas.LinkedDatasetSchema().load(linked_dataset_data)
