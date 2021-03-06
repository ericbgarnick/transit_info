import marshmallow as mm
import typing
from marshmallow_enum import EnumField

from flaskr import schema_utils
from tests import models as test_models


class GeoStubSchema(mm.Schema):
    geo_stub_id = mm.fields.Int(required=True)
    longitude = mm.fields.Float(required=True)
    latitude = mm.fields.Float(required=True)

    @mm.post_load
    def make_geo_stub(self, data: typing.Dict, **kwargs) -> test_models.GeoStub:
        return test_models.GeoStub(
            geo_stub_id=data.pop("geo_stub_id"),
            longitude=data.pop("longitude"),
            latitude=data.pop("latitude"),
        )


class TestModelSchema(mm.Schema):
    SKIP_ID = "skip_me"
    test_id = mm.fields.Str(required=True)  # Use test_id = SKIP_ID to skip an instance
    test_name = mm.fields.Str(required=True)
    test_type = EnumField(test_models.TestType, required=True)
    test_order = mm.fields.Int(required=False)
    test_dist = mm.fields.Float(required=False)
    geo_stub_id = mm.fields.Int(required=False)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["test_type"] = schema_utils.numbered_type_enum_key(in_data["test_type"])
        return {k: v for k, v in in_data.items() if v}

    def load(self, *args, **kwargs) -> typing.Optional[test_models.TestModel]:
        data = args[0]
        if data["test_id"] == self.SKIP_ID:
            return None
        else:
            return super().load(*args, **kwargs)

    @mm.post_load
    def make_test_model(self, data: typing.Dict, **kwargs) -> test_models.TestModel:
        return test_models.TestModel(
            data.pop("test_id"), data.pop("test_name"), data.pop("test_type"), **data
        )
