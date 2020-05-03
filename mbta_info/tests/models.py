"""
Models used for testing independent of real data models
"""
import typing
import geoalchemy2

from mbta_info.flaskr.database import db
from mbta_info.flaskr import models


class GeoStub(db.Model, models.GeoMixin):
    lonlat_field = "lonlat_column"

    lonlat_column = db.Column(geoalchemy2.Geometry("POINT"), primary_key=True)

    def __init__(self, lonlat_val: typing.Tuple[float, float]):
        lon, lat = lonlat_val
        self.lonlat_column = f"POINT({lon} {lat})"
