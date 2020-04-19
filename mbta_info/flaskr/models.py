import datetime
import enum
import logging
from typing import Tuple, Optional

import pycountry
import pytz
from geoalchemy2 import Geometry
from sqlalchemy import func, inspect
from sqlalchemy.exc import DataError

from mbta_info.flaskr.app import db

logger = logging.getLogger(__name__)

# noinspection PyTypeChecker
TimeZone = enum.Enum('TimeZone', {tz.replace('/', '_'): tz for tz in pytz.all_timezones})
# noinspection PyTypeChecker
LangCode = enum.Enum('LangCode', {
    lang.alpha_2: lang.alpha_2 for lang in pycountry.languages if getattr(lang, 'alpha_2', None)
})


class GeoMixin:
    _longitude_cache = None
    _latitude_cache = None

    @property
    def longitude(self) -> float:
        if self._longitude_cache is None:
            self._longitude_cache, self._latitude_cache = self.lonlat
        return self._longitude_cache

    @property
    def latitude(self) -> float:
        if self._latitude_cache is None:
            self._longitude_cache, self._latitude_cache = self.lonlat
        return self._latitude_cache

    @property
    def lonlat(self) -> Optional[Tuple[float, float]]:
        """
        Return a tuple of (lon, lat) or return None and log exception if no coordinates can be retrieved.

        Note: Should only be called if self._longitude_cache and self._latitude_cache are not set
        """
        lonlat_value = getattr(self, self.lonlat_field)
        try:
            lon, lat = db.session.query(func.ST_X(lonlat_value), func.ST_Y(lonlat_value)).first()
            db.session.close()
            return lon, lat
        except DataError:
            logger.exception(f"Failed to get lon, lat for Shape {inspect(self).identity[0]}")
            db.session.close()

    @property
    def lonlat_field(self) -> str:
        """Return the name of the field where longitude and latitude are stored"""
        raise NotImplementedError


class Agency(db.Model):
    """
    A transit agency
    Requires: agency_id, agency_name, agency_url, agency_timezone
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#agencytxt
    """
    agency_id = db.Column(db.Integer, primary_key=True)
    agency_name = db.Column(db.String(16), nullable=False, unique=True)
    agency_url = db.Column(db.String(64), nullable=False, unique=True)
    agency_timezone = db.Column(db.Enum(TimeZone), nullable=False)
    agency_lang = db.Column(db.Enum(LangCode), nullable=True)
    agency_phone = db.Column(db.String(16), nullable=True)
    routes = db.relationship('Route', backref='agency', lazy=True)

    def __init__(self, agency_id: int, name: str, url: str, timezone: TimeZone, **kwargs):
        self.agency_id = agency_id
        self.agency_name = name
        self.agency_url = url
        self.agency_timezone = timezone

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Agency: {self.agency_name}>'


class Line(db.Model):
    """
    A transit line
    Requires: line_id, line_long_name
    Relies on: None
    Reference: None
    """
    line_id = db.Column(db.String(32), primary_key=True)
    line_short_name = db.Column(db.String(16), nullable=True)
    line_long_name = db.Column(db.String(128), nullable=False)
    line_desc = db.Column(db.String(32), nullable=True)
    line_url = db.Column(db.String(64), nullable=True)
    line_color = db.Column(db.String(8), nullable=True)
    line_text_color = db.Column(db.String(8), nullable=True)
    line_sort_order = db.Column(db.Integer, nullable=True)
    routes = db.relationship('Route', backref='line', lazy=True)

    def __init__(self, line_id: str, long_name: str, **kwargs):
        self.line_id = line_id
        self.line_long_name = long_name

        for fieldname, value in kwargs.items():
            if fieldname != 'routes':
                setattr(self, fieldname, value)

        # TODO: Is this right?  Seems like it might not be
        for route in kwargs.get('routes', []):
            route.line_id = self.line_id
            db.session.add(route)
        db.session.commit()

    def __repr__(self):
        return f'<Line: {self.line_id}>'


class RouteType(enum.Enum):
    type_0 = 'street_level_rail'
    type_1 = 'underground_rail'
    type_2 = 'long_dist_rail'
    type_3 = 'bus'
    type_4 = 'ferry'
    type_5 = 'cable_tram'
    type_6 = 'suspended'
    type_7 = 'funicular'
    type_11 = 'trolleybus'
    type_12 = 'monorail'


class FareClass(enum.Enum):
    rapid_transit = 0
    local_bus = 1
    commuter_rail = 2
    ferry = 3
    inner_express = 4
    outer_express = 5
    free = 6


class Route(db.Model):
    """
    A transit route
    Requires: route_id, agency_id, route_long_name, route_type
    Relies on: Agency, Line
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#routestxt
    """
    route_id = db.Column(db.String(64), primary_key=True)
    agency_id = db.Column(db.ForeignKey('agency.agency_id'), nullable=False)
    route_short_name = db.Column(db.String(16), nullable=True)
    route_long_name = db.Column(db.String(128), nullable=False)
    route_desc = db.Column(db.String(32), nullable=True)
    route_type = db.Column(db.Enum(RouteType), nullable=False)
    route_url = db.Column(db.String(64), nullable=True)
    route_color = db.Column(db.String(8), nullable=True)
    route_text_color = db.Column(db.String(8), nullable=True)
    route_sort_order = db.Column(db.Integer, nullable=True)
    route_fare_class = db.Column(db.Enum(FareClass), nullable=True)
    line_id = db.Column(db.String(32), db.ForeignKey('line.line_id'), nullable=True)

    def __init__(self, route_id: str, agency_id: int, long_name: str, route_type: RouteType, **kwargs):
        self.route_id = route_id
        self.agency_id = agency_id
        self.route_long_name = long_name
        self.route_type = route_type

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Route: {self.route_id}>'


class LocationType(enum.Enum):
    type_0 = 'stop_or_platform'  # Default when no value given (platform when defined within a parent station)
    type_1 = 'station'           # A physical structure or area that contains one or more platform
    type_2 = 'entrance_exit'     # A location where passengers can enter or exit a station from the street
    type_3 = 'generic_node'      # A location within a station not matching any other LocationType
    type_4 = 'boarding_area'     # A specific location on a platform where passengers can board and/or alight vehicles


class AccessibilityType(enum.Enum):
    type_0 = 'unknown_or_inherited'  # Default when no value given.  Inherited when Stop has a parent
    type_1 = 'limited_or_full'
    type_2 = 'inaccessible'


class Stop(db.Model, GeoMixin):
    """
    A transit stop
    Requires: stop_id
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#stopstxt
    """
    stop_id = db.Column(db.String(64), primary_key=True)
    stop_code = db.Column(db.String(64), nullable=True)  # Often the same as stop_id (or shortened version thereof)
    stop_name = db.Column(db.String(128), nullable=True)
    tts_stop_name = db.Column(db.String(64), nullable=True)  # Defaults to stop_name - used to resolve TTS ambiguities
    stop_desc = db.Column(db.String(256), nullable=True)
    platform_code = db.Column(db.String(8), nullable=True)
    platform_name = db.Column(db.String(64), nullable=True)
    # to retrieve lon, lat: db.session.query(func.ST_X(Stop.stop_lonlat), func.ST_Y(Stop.stop_lonlat)).first()
    stop_lonlat = db.Column(Geometry('POINT'), nullable=True)
    zone_id = db.Column(db.String(32), nullable=True)
    stop_address = db.Column(db.String(128), nullable=True)
    stop_url = db.Column(db.String(64), nullable=True)
    level_id = db.Column(db.String(64), nullable=True)
    location_type = db.Column(db.Enum(LocationType), nullable=True)
    parent_station = db.Column(db.String(64), db.ForeignKey('stop.stop_id'), nullable=True)
    wheelchair_boarding = db.Column(db.Enum(AccessibilityType), nullable=True)
    municipality = db.Column(db.String(64), nullable=True)
    on_street = db.Column(db.String(64), nullable=True)
    at_street = db.Column(db.String(64), nullable=True)
    vehicle_type = db.Column(db.Enum(RouteType), nullable=True)
    stop_timezone = db.Column(db.Enum(TimeZone), nullable=True)  # Inherits from Agency.agency_timezone if null

    def __init__(self, stop_id: str, **kwargs):
        self.stop_id = stop_id

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Stop: {self.stop_id}: {self.stop_name}>'

    @property
    def lonlat_field(self) -> str:
        """Return the name of the field where longitude and latitude are stored"""
        return 'stop_lonlat'


class Calendar(db.Model):
    """
    Identifies the days of service within a given date range
    Requires: service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#calendartxt
    """
    service_id = db.Column(db.String(64), primary_key=True)
    monday = db.Column(db.Boolean(), nullable=False)
    tuesday = db.Column(db.Boolean(), nullable=False)
    wednesday = db.Column(db.Boolean(), nullable=False)
    thursday = db.Column(db.Boolean(), nullable=False)
    friday = db.Column(db.Boolean(), nullable=False)
    saturday = db.Column(db.Boolean(), nullable=False)
    sunday = db.Column(db.Boolean(), nullable=False)
    start_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date(), nullable=False)

    def __init__(self, service_id: str, monday: bool, tuesday: bool, wednesday: bool, thursday: bool,  friday: bool,
                 saturday: bool, sunday: bool, start_date: datetime.date, end_date: datetime.date):
        self.service_id = service_id
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f'<Calendar: {self.service_id} ({self.start_date}-{self.end_date})>'


class Shape(db.Model, GeoMixin):
    """
    A rule for mapping vehicle travel paths, sometimes referred to as a route alignment
    Requires: shape_id, shape_pt_lon, shape_pt_lat, shape_pt_sequence
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#shapestxt
    """
    shape_id = db.Column(db.String(64), primary_key=True)
    shape_pt_lonlat = db.Column(Geometry('POINT'), nullable=False)
    shape_pt_sequence = db.Column(db.Integer())  # Increasing but not necessarily consecutive for each subsequent stop
    shape_dist_traveled = db.Column(db.Float())

    def __init__(self, shape_id: str, shape_pt_lon: float, shape_pt_lat: float, shape_pt_sequence: int, **kwargs):
        self._longitude_cache = shape_pt_lon
        self._latitude_cache = shape_pt_lat
        self.shape_id = shape_id
        self.shape_pt_lonlat = f'POINT({shape_pt_lon} {shape_pt_lat})'
        self.shape_pt_sequence = shape_pt_sequence

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Shape: {self.shape_id} @ ({self.longitude}, {self.latitude})>'

    @property
    def lonlat_field(self) -> str:
        """Return the name of the field where longitude and latitude are stored"""
        return 'shape_pt_lonlat'


# class Trip(db.Model):
#     """
#     A trip for a route in a transit system. A trip is a sequence
#     of two or more stops that occur during a specific time period.
#     Requires: route_id, service_id, trip_id
#     Relies on: Route, Calendar, Shape
#     Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#tripstxt
#     """
#     pass
