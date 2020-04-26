from typing import Tuple

from geoalchemy2 import Geometry

from mbta_info.flaskr.models import GeoMixin
from mbta_info.flaskr.app import db


class GeoStub(db.Model, GeoMixin):
    lonlat_field = 'lonlat_column'

    lonlat_column = db.Column(Geometry("POINT"), primary_key=True)

    def __init__(self, lonlat_val: Tuple[float, float]):
        lon, lat = lonlat_val
        self.lonlat_column = f"POINT({lon} {lat})"


def test_lonlat_from_cache(monkeypatch):
    """longitude and latitude values are returned from cache without using lonlat property"""
    longitude = 1.0
    latitude = 2.0

    monkeypatch.setattr(GeoMixin, 'lonlat', ("no_cache", "no_cache"))

    geomixin = GeoMixin()
    geomixin._longitude_cache = longitude
    geomixin._latitude_cache = latitude

    assert geomixin.longitude == longitude
    assert geomixin.latitude == latitude


def test_lonlat_from_field():
    """longitude and latitude values are retrieved from db column value and cache attributes are populated"""
    longitude = 1.0
    latitude = 2.0

    geo_stub = GeoStub((longitude, latitude))

    # Retrieves correct value and populates cache attrs
    assert geo_stub.longitude == geo_stub._longitude_cache == longitude
    assert geo_stub.latitude == geo_stub._latitude_cache == latitude
