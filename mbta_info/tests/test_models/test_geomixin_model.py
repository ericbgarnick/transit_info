from mbta_info.flaskr import models as mbta_models
from mbta_info.tests import models as test_models


def test_lonlat_from_cache(monkeypatch):
    """longitude and latitude values are returned from cache without using lonlat property"""
    longitude = 1.0
    latitude = 2.0

    monkeypatch.setattr(mbta_models.GeoMixin, "lonlat", ("no_cache", "no_cache"))

    geomixin = mbta_models.GeoMixin()
    geomixin._longitude_cache = longitude
    geomixin._latitude_cache = latitude

    assert geomixin.longitude == longitude
    assert geomixin.latitude == latitude


def test_lonlat_from_field(app):
    """longitude and latitude values are retrieved from db column value and cache attributes are populated"""
    longitude = 1.0
    latitude = 2.0

    geo_stub = test_models.GeoStub(1, longitude, latitude)

    # Retrieves correct value and populates cache attrs
    assert geo_stub.longitude == geo_stub._longitude_cache == longitude
    assert geo_stub.latitude == geo_stub._latitude_cache == latitude
