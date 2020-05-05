import datetime
import enum
import logging
import typing

import pycountry
import pytz
from geoalchemy2 import Geometry
from sqlalchemy import func, inspect
from sqlalchemy.exc import DataError

from mbta_info.flaskr.database import db

logger = logging.getLogger(__name__)

TimeZone = enum.Enum(  # type: ignore[misc]
    "TimeZone", {tz.replace("/", "_"): tz for tz in pytz.all_timezones}
)
LangCode = enum.Enum(  # type: ignore[misc]
    "LangCode",
    {
        lang.alpha_2: lang.alpha_2
        for lang in pycountry.languages
        if getattr(lang, "alpha_2", None)
    },
)


class GeoMixin:
    """A mixin class for models having a Geometry POINT field - allows convenient, cached access to lon/lat values"""

    lonlat_field: typing.ClassVar[str]
    _longitude_cache: typing.Optional[float] = None
    _latitude_cache: typing.Optional[float] = None

    @property
    def longitude(self) -> typing.Optional[float]:
        if self._longitude_cache is None:
            self._longitude_cache, self._latitude_cache = self.lonlat
        return self._longitude_cache

    @property
    def latitude(self) -> typing.Optional[float]:
        if self._latitude_cache is None:
            self._longitude_cache, self._latitude_cache = self.lonlat
        return self._latitude_cache

    @property
    def lonlat(
        self,
    ) -> typing.Union[typing.Tuple[None, None], typing.Tuple[float, float]]:
        """
        Return a tuple of (lon, lat) or return None and log exception if no coordinates can be retrieved.

        Note: Should only be called if self._longitude_cache and self._latitude_cache are not set
        """
        lonlat_value = getattr(self, self.lonlat_field)
        try:
            lon, lat = db.session.query(
                func.ST_X(lonlat_value), func.ST_Y(lonlat_value)
            ).first()
        except DataError:
            logger.exception(
                f"Failed to get lon, lat for Shape {inspect(self).identity[0]}"
            )
            lon, lat = None, None
        finally:
            db.session.close()
        return lon, lat


class Agency(db.Model):
    """
    A transit agency
    Requires: agency_id, agency_name, agency_url, agency_timezone
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#agencytxt
    """

    agency_id = db.Column(db.Integer, primary_key=True)
    agency_name = db.Column(db.String(64), nullable=False, unique=True)
    agency_url = db.Column(db.String(64), nullable=False, unique=True)
    agency_timezone = db.Column(db.Enum(TimeZone), nullable=False)
    agency_lang = db.Column(db.Enum(LangCode), nullable=True)
    agency_phone = db.Column(db.String(16), nullable=True)

    def __init__(
        self, agency_id: int, name: str, url: str, timezone: TimeZone, **kwargs
    ):
        self.agency_id = agency_id
        self.agency_name = name
        self.agency_url = url
        self.agency_timezone = timezone

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Agency: {self.agency_id} ({self.agency_name})>"


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

    def __init__(self, line_id: str, long_name: str, **kwargs):
        self.line_id = line_id
        self.line_long_name = long_name

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Line: {self.line_id}>"


class RouteType(enum.Enum):
    type_0 = "street_level_rail"
    type_1 = "underground_rail"
    type_2 = "long_dist_rail"
    type_3 = "bus"
    type_4 = "ferry"
    type_5 = "cable_tram"
    type_6 = "suspended"
    type_7 = "funicular"
    type_11 = "trolleybus"
    type_12 = "monorail"


class FareClass(enum.Enum):
    rapid_transit = 0
    local_bus = 1
    commuter_rail = 2
    ferry = 3
    inner_express = 4
    outer_express = 5
    free = 6
    special = 7


class Route(db.Model):
    """
    A transit route
    Requires: route_id, agency_id, route_long_name, route_type
    Relies on: Agency, Line
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#routestxt
    """

    route_id = db.Column(db.String(64), primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.agency_id"), nullable=False)
    agency = db.relationship("Agency", backref="routes")
    route_short_name = db.Column(db.String(16), nullable=True)
    route_long_name = db.Column(db.String(128), nullable=False)
    route_desc = db.Column(db.String(32), nullable=True)
    route_type = db.Column(db.Enum(RouteType), nullable=False)
    route_url = db.Column(db.String(64), nullable=True)
    route_color = db.Column(db.String(8), nullable=True)
    route_text_color = db.Column(db.String(8), nullable=True)
    route_sort_order = db.Column(db.Integer, nullable=True)
    route_fare_class = db.Column(db.Enum(FareClass), nullable=True)
    line_id = db.Column(db.String(32), db.ForeignKey("line.line_id"), nullable=True)
    line = db.relationship("Line", backref="routes")

    def __init__(
        self,
        route_id: str,
        agency_id: int,
        long_name: str,
        route_type: RouteType,
        **kwargs,
    ):
        self.route_id = route_id
        self.agency_id = agency_id
        self.route_long_name = long_name
        self.route_type = route_type

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Route: {self.route_id}>"


class LocationType(enum.Enum):
    type_0 = "stop_or_platform"  # Default when no value given (platform when defined within a parent station)
    type_1 = (
        "station"  # A physical structure or area that contains one or more platform
    )
    type_2 = "entrance_exit"  # A location where passengers can enter or exit a station from the street
    type_3 = "generic_node"  # A location within a station not matching any other LocationType
    type_4 = "boarding_area"  # A specific location on a platform where passengers can board and/or alight vehicles


class AccessibilityType(enum.Enum):
    type_0 = "unknown_or_inherited"  # Default when no value given.  Inherited when Stop has a parent
    type_1 = "limited_or_full"
    type_2 = "inaccessible"


class Stop(db.Model, GeoMixin):
    """
    A transit stop
    Requires: stop_id
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#stopstxt
    """

    lonlat_field = "stop_lonlat"

    stop_id = db.Column(db.String(64), primary_key=True)
    stop_code = db.Column(
        db.String(64), nullable=True
    )  # Often the same as stop_id (or shortened version thereof)
    stop_name = db.Column(db.String(128), nullable=True)
    tts_stop_name = db.Column(
        db.String(64), nullable=True
    )  # Defaults to stop_name - used to resolve TTS ambiguities
    stop_desc = db.Column(db.String(256), nullable=True)
    platform_code = db.Column(db.String(8), nullable=True)
    platform_name = db.Column(db.String(64), nullable=True)
    # to retrieve lon, lat: db.session.query(func.ST_X(Stop.stop_lonlat), func.ST_Y(Stop.stop_lonlat)).first()
    stop_lonlat = db.Column(Geometry("POINT"), nullable=True, index=True)
    zone_id = db.Column(db.String(32), nullable=True)
    stop_address = db.Column(db.String(128), nullable=True)
    stop_url = db.Column(db.String(64), nullable=True)
    level_id = db.Column(db.String(64), nullable=True)
    location_type = db.Column(db.Enum(LocationType), nullable=True)
    parent_station = db.Column(
        db.String(64), db.ForeignKey("stop.stop_id"), nullable=True
    )
    parent = db.relationship("Stop", backref="children", remote_side=[stop_id])
    wheelchair_boarding = db.Column(db.Enum(AccessibilityType), nullable=True)
    municipality = db.Column(db.String(64), nullable=True)
    on_street = db.Column(db.String(64), nullable=True)
    at_street = db.Column(db.String(64), nullable=True)
    vehicle_type = db.Column(db.Enum(RouteType), nullable=True)
    stop_timezone = db.Column(
        db.Enum(TimeZone), nullable=True
    )  # Inherits from Agency.agency_timezone if null

    def __init__(self, stop_id: str, **kwargs):
        self.stop_id = stop_id

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Stop: {self.stop_id} ({self.stop_name})>"


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

    def __init__(
        self,
        service_id: str,
        monday: bool,
        tuesday: bool,
        wednesday: bool,
        thursday: bool,
        friday: bool,
        saturday: bool,
        sunday: bool,
        start_date: datetime.date,
        end_date: datetime.date,
    ):
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
        return f"<Calendar: {self.service_id} ({self.start_date}-{self.end_date})>"


class Shape(db.Model, GeoMixin):
    """
    A rule for mapping vehicle travel paths, sometimes referred to as a route alignment
    Requires: shape_id, shape_pt_lon, shape_pt_lat, shape_pt_sequence
    Relies on: None
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#shapestxt
    """

    lonlat_field = "shape_pt_lonlat"

    id = db.Column(db.Integer, primary_key=True)
    shape_id = db.Column(db.String(64), nullable=False, index=True)
    shape_pt_lonlat = db.Column(Geometry("POINT"), nullable=False)
    # Increasing but not necessarily consecutive for each subsequent stop
    shape_pt_sequence = db.Column(db.Integer(), nullable=False)
    shape_dist_traveled = db.Column(db.Float(), nullable=True)

    def __init__(
        self,
        shape_id: str,
        shape_pt_lon: float,
        shape_pt_lat: float,
        shape_pt_sequence: int,
        **kwargs,
    ):
        self._longitude_cache = shape_pt_lon
        self._latitude_cache = shape_pt_lat
        self.shape_id = shape_id
        self.shape_pt_lonlat = f"POINT({shape_pt_lon} {shape_pt_lat})"
        self.shape_pt_sequence = shape_pt_sequence

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Shape: {self.shape_id} @ ({self.longitude}, {self.latitude})>"


class Direction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String(64), db.ForeignKey("route.route_id"), nullable=False)
    route = db.relationship("Route", backref="directions")
    direction_id = db.Column(db.SmallInteger, nullable=False)
    direction = db.Column(db.String(16), nullable=False)
    direction_destination = db.Column(db.String(64), nullable=False)

    def __init__(
        self,
        route_id: str,
        direction_id: int,
        direction: str,
        direction_destination: str,
    ):
        self.route_id = route_id
        self.direction_id = direction_id
        self.direction = direction
        self.direction_destination = direction_destination

    def __repr__(self):
        return f"<Direction: {self.route_id} ({self.direction} -> {self.direction_destination})>"


class RoutePattern(db.Model):
    """
    For a given route, each pair of start and end stops generally has 2 RoutePatterns - one going each direction
    Requires: route_pattern_id, route_id
    Relies on: Route, Trip
    Reference: None
    """

    route_pattern_id = db.Column(db.String(64), primary_key=True)
    route_id = db.Column(
        db.String(64), db.ForeignKey("route.route_id"), nullable=False, index=True
    )
    route = db.relationship("Route", backref="patterns")
    direction_id = db.Column(db.SmallInteger, nullable=True)  # 0 or 1
    route_pattern_name = db.Column(db.String(128), nullable=True)
    route_pattern_time_desc = db.Column(db.String(32), nullable=True)
    route_pattern_typicality = db.Column(db.Integer, nullable=True)
    route_pattern_sort_order = db.Column(db.Integer, nullable=True)
    representative_trip_id = db.Column(
        db.String(128), nullable=True
    )  # Not a FK because use isn't clear

    def __init__(self, route_pattern_id: str, route_id: str, **kwargs):
        self.route_pattern_id = route_pattern_id
        self.route_id = route_id

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<RoutePattern: {self.route_pattern_id} (Route: {self.route_id})>"


class TripAccessibility(enum.Enum):
    type_0 = "unknown"  # Default when no value given
    type_1 = "one_or_more"  # One or more bikes or wheelchairs can be accommodated on this trip
    type_2 = "none"  # No bikes or wheelchairs can be accommodated on this trip


class Trip(db.Model):
    """
    A trip for a route in a transit system. A trip is a sequence
    of two or more stops that occur during a specific time period.
    Requires: route_id, service_id, trip_id
    Relies on: Route, Calendar, RoutePattern
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#tripstxt
    """

    trip_id = db.Column(db.String(128), primary_key=True)
    route_id = db.Column(
        db.String(64), db.ForeignKey("route.route_id"), nullable=False, index=True
    )
    route = db.relationship("Route", backref="trips")
    service_id = db.Column(
        db.String(64), db.ForeignKey("calendar.service_id"), nullable=False, index=True
    )
    service = db.relationship("Calendar", backref="trips")
    trip_headsign = db.Column(db.String(128), nullable=True)
    trip_short_name = db.Column(db.String(16), nullable=True)
    direction_id = db.Column(db.SmallInteger(), nullable=True)  # 0 or 1
    block_id = db.Column(db.String(64), nullable=True)
    shape_id = db.Column(db.String(64), nullable=True)
    wheelchair_accessible = db.Column(db.Enum(TripAccessibility), nullable=True)
    trip_route_type = db.Column(db.Enum(RouteType), nullable=True)
    route_pattern_id = db.Column(
        db.String(64), db.ForeignKey("route_pattern.route_pattern_id"), nullable=True
    )
    route_pattern = db.relationship("RoutePattern", backref="trips")
    bikes_allowed = db.Column(db.Enum(TripAccessibility), nullable=True)

    def __init__(self, trip_id: str, route_id: str, service_id: str, **kwargs):
        self.trip_id = trip_id
        self.route_id = route_id
        self.service_id = service_id

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f"<Trip: {self.trip_id} (Route: {self.route_id} @ {self.service_id})>"


class Checkpoint(db.Model):
    checkpoint_id = db.Column(db.String(16), primary_key=True)
    checkpoint_name = db.Column(db.String(128), nullable=False)

    def __init__(self, checkpoint_id: str, checkpoint_name: str):
        self.checkpoint_id = checkpoint_id
        self.checkpoint_name = checkpoint_name

    def __repr__(self):
        return f"<Checkpoint: {self.checkpoint_id}>"


class PickupDropOffType(enum.Enum):
    type_0 = "regularly_scheduled"
    type_1 = "none_available"
    type_2 = "arrange_with_agency"
    type_3 = "arrange_with_driver"


class StopTime(db.Model):
    """
    Times that a vehicle arrives at and departs from stops for each trip.
    Requires: trip_id, arrival_time, departure_time, stop_id, stop_sequence
    Relies on: Trip, Stop
    Reference: https://github.com/google/transit/blob/master/gtfs/spec/en/reference.md#stop_timestxt
    """

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(128), db.ForeignKey("trip.trip_id"), nullable=False)
    trip = db.relationship("Trip", backref="times")
    arrival_time = db.Column(db.Integer(), nullable=False)  # Seconds since 00:00:00
    departure_time = db.Column(db.Integer(), nullable=False)  # Seconds since 00:00:00
    stop_id = db.Column(db.String(64), db.ForeignKey("stop.stop_id"), nullable=False)
    stop = db.relationship("Stop", backref="times")
    stop_sequence = db.Column(db.Integer(), nullable=False)
    stop_headsign = db.Column(db.String(128), nullable=True)
    pickup_type = db.Column(db.Enum(PickupDropOffType), nullable=True)
    drop_off_type = db.Column(db.Enum(PickupDropOffType), nullable=True)
    shape_dist_traveled = db.Column(
        db.Float(), nullable=True
    )  # Distance traveled from the first stop to this stop
    timepoint = db.Column(
        db.SmallInteger(), nullable=True
    )  # 0 = times are approximate, 1 = times are exact
    checkpoint_id = db.Column(
        db.String(16), nullable=True
    )  # References table PK, but not a FK because unknown usage

    def __init__(
        self,
        trip_id: str,
        arrival_time: datetime.time,
        departure_time: datetime.time,
        stop_id: str,
        stop_sequence: int,
        **kwargs,
    ):
        self.trip_id = trip_id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.stop_id = stop_id
        self.stop_sequence = stop_sequence

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return (
            f"<StopTime: {self.arrival_time}->{self.departure_time} @ {self.stop_id}>"
        )
