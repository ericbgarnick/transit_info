"""
Models used for testing independent of real data models
"""
import enum
import geoalchemy2

from mbta_info.flaskr.database import db
from mbta_info.flaskr import models


class GeoStub(db.Model, models.GeoMixin):
    lonlat_field = "lonlat_column"

    geo_stub_id = db.Column(db.Integer, primary_key=True)
    lonlat_column = db.Column(geoalchemy2.Geometry("POINT"))

    def __init__(self, geo_stub_id: int, longitude: float, latitude: float):
        self.geo_stub_id = geo_stub_id
        self.lonlat_column = f"POINT({longitude} {latitude})"


class TestType(enum.Enum):
    type_0 = "zero"
    type_1 = "one"
    type_2 = "two"


class TestModel(db.Model):
    """
    A model for tools and utilities that operate on models.
    Has Integer, String, Float and Enum fields
    """

    test_id = db.Column(db.String(32), primary_key=True)
    test_name = db.Column(db.String(64), nullable=False, unique=True)
    test_type = db.Column(db.Enum(TestType), nullable=False)
    test_order = db.Column(db.Integer, nullable=True)
    test_dist = db.Column(db.Float, nullable=True)
    geo_stub_id = db.Column(
        db.Integer, db.ForeignKey("geo_stub.geo_stub_id"), nullable=True
    )
    geo_stub = db.relationship("GeoStub", backref="test_models")

    def __init__(self, test_id: str, test_name: str, test_type: TestType, **kwargs):
        self.test_id = test_id
        self.test_name = test_name
        self.test_type = test_type

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<TestModel: {self.test_id} ({self.test_name})>"
