import logging
from typing import Dict, Optional

from marshmallow import Schema, pre_load, post_load, fields as mm_fields, ValidationError
from marshmallow_enum import EnumField

from mbta_info.flaskr.models import (
    Agency, Line, Route, TimeZone, LangCode, RouteType, FareClass, LocationType, AccessibilityType, Stop, Calendar,
    Shape, TripAccessibility, Trip, RoutePattern, PickupDropOffType, StopTime, Checkpoint, Direction
)
from mbta_info.flaskr.schema_utils import time_as_seconds, numbered_type_enum_key, timezone_enum_key
from mbta_info.flaskr import fields as mbta_fields

logger = logging.getLogger(__name__)


class AgencySchema(Schema):
    agency_id = mm_fields.Int(required=True)
    agency_name = mm_fields.Str(required=True)
    agency_url = mm_fields.Url(required=True)
    agency_timezone = EnumField(TimeZone, required=True)
    agency_lang = EnumField(LangCode)
    agency_phone = mm_fields.Str()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        in_data['agency_timezone'] = timezone_enum_key(in_data['agency_timezone'])
        in_data['agency_lang'] = in_data.get('agency_lang', '').lower()
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_agency(self, data: Dict, **kwargs) -> Agency:
        return Agency(
            data.pop('agency_id'),
            data.pop('agency_name'),
            data.pop('agency_url'),
            data.pop('agency_timezone'),
            **data
        )


class LineSchema(Schema):
    line_id = mm_fields.Str(required=True)
    line_short_name = mm_fields.Str()
    line_long_name = mm_fields.Str(required=True)
    line_desc = mm_fields.Str()
    line_url = mm_fields.Url()
    line_color = mm_fields.Str()
    line_text_color = mm_fields.Str()
    line_sort_order = mm_fields.Int()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_line(self, data: Dict, **kwargs) -> Line:
        return Line(
            data.pop('line_id'),
            data.pop('line_long_name'),
            **data
        )


class RouteSchema(Schema):
    route_id = mm_fields.Str(required=True)
    agency_id = mm_fields.Int(required=True)
    route_short_name = mm_fields.Str()
    route_long_name = mm_fields.Str(required=True)
    route_desc = mm_fields.Str()
    route_type = EnumField(RouteType, required=True)
    route_url = mm_fields.Url()
    route_color = mm_fields.Str()
    route_text_color = mm_fields.Str()
    route_sort_order = mm_fields.Int()
    route_fare_class = EnumField(FareClass)
    line_id = mm_fields.Str()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        in_data.pop('listed_route', None)
        in_data['route_fare_class'] = in_data['route_fare_class'].replace(' ', '_').lower()
        in_data['route_type'] = numbered_type_enum_key(in_data['route_type'])
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_route(self, data: Dict, **kwargs) -> Route:
        return Route(
            data.pop('route_id'),
            data.pop('agency_id'),
            data.pop('route_long_name'),
            data.pop('route_type'),
            **data
        )


class StopSchema(Schema):
    stop_id = mm_fields.Str(required=True)
    stop_code = mm_fields.Str()
    stop_name = mm_fields.Str()
    tts_stop_name = mm_fields.Str()
    stop_desc = mm_fields.Str()
    platform_code = mm_fields.Str()
    platform_name = mm_fields.Str()
    stop_lat = mm_fields.Float()
    stop_lon = mm_fields.Float()
    zone_id = mm_fields.Str()
    stop_address = mm_fields.Str()
    stop_url = mm_fields.Url()
    level_id = mm_fields.Str()
    location_type = EnumField(LocationType)
    parent_station = mm_fields.Str()
    wheelchair_boarding = EnumField(AccessibilityType)
    municipality = mm_fields.Str()
    on_street = mm_fields.Str()
    at_street = mm_fields.Str()
    vehicle_type = EnumField(RouteType)
    stop_timezone = EnumField(TimeZone)

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        in_data['location_type'] = numbered_type_enum_key(in_data['location_type'], default_0=True)
        in_data['wheelchair_boarding'] = numbered_type_enum_key(in_data['wheelchair_boarding'], default_0=True)
        in_data['vehicle_type'] = numbered_type_enum_key(in_data['vehicle_type'])
        in_data['stop_timezone'] = timezone_enum_key(in_data.get('stop_timezone'))
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_stop(self, data: Dict, **kwargs) -> Stop:
        try:
            lon = data.pop('stop_lon')
            lat = data.pop('stop_lat')
            data['stop_lonlat'] = f'POINT({lon} {lat})'
        except KeyError:
            pass
        return Stop(
            data.pop('stop_id'),
            **data
        )


class CalendarSchema(Schema):
    DATE_INPUT_FORMAT = '%Y%m%d'

    service_id = mm_fields.Str(required=True)
    monday = mm_fields.Bool(required=True)
    tuesday = mm_fields.Bool(required=True)
    wednesday = mm_fields.Bool(required=True)
    thursday = mm_fields.Bool(required=True)
    friday = mm_fields.Bool(required=True)
    saturday = mm_fields.Bool(required=True)
    sunday = mm_fields.Bool(required=True)
    start_date = mm_fields.Date(format=DATE_INPUT_FORMAT, required=True)
    end_date = mm_fields.Date(format=DATE_INPUT_FORMAT, required=True)

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            in_data[day] = bool(int(in_data[day]))
        return in_data

    @post_load
    def make_calendar(self, data: Dict, **kwargs) -> Calendar:
        return Calendar(
            data.pop('service_id'),
            data.pop('monday'),
            data.pop('tuesday'),
            data.pop('wednesday'),
            data.pop('thursday'),
            data.pop('friday'),
            data.pop('saturday'),
            data.pop('sunday'),
            data.pop('start_date'),
            data.pop('end_date'),
        )


class ShapeSchema(Schema):
    shape_id = mm_fields.Str(required=True)
    shape_pt_lat = mm_fields.Float(required=True)
    shape_pt_lon = mm_fields.Float(required=True)
    shape_pt_sequence = mm_fields.Int(required=True)
    shape_dist_traveled = mm_fields.Float()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_shape(self, data: Dict, **kwargs) -> Shape:
        return Shape(
            data.pop('shape_id'),
            data.pop('shape_pt_lon'),
            data.pop('shape_pt_lat'),
            data.pop('shape_pt_sequence'),
            **data
        )


class DirectionSchema(Schema):
    route_id = mbta_fields.RouteId(required=True)
    direction_id = mm_fields.Int(required=True)
    direction = mm_fields.Str(required=True)
    direction_destination = mm_fields.Str(required=True)

    def load(self, *args, **kwargs) -> Optional[Direction]:
        """Load direction data, skipping rows that reference non-existent Routes"""
        try:
            return super().load(*args, **kwargs)
        except ValidationError as ve:
            if mbta_fields.RouteId.is_missing_route_error(ve):
                logger.info(ve.normalized_messages())
                return None
            else:
                raise ve

    @post_load
    def make_direction(self, data: Dict, **kwargs) -> Direction:
        return Direction(
            route_id=data.pop('route_id'),
            direction_id=data.pop('direction_id'),
            direction=data.pop('direction'),
            direction_destination=data.pop('direction_destination')
        )


class RoutePatternSchema(Schema):
    route_pattern_id = mm_fields.Str(required=True)
    route_id = mm_fields.Str(required=True)
    direction_id = mm_fields.Int()
    route_pattern_name = mm_fields.Str()
    route_pattern_time_desc = mm_fields.Str()
    route_pattern_typicality = mm_fields.Int()
    route_pattern_sort_order = mm_fields.Int()
    representative_trip_id = mm_fields.Str()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_route_pattern(self, data: Dict, **kwargs) -> RoutePattern:
        return RoutePattern(
            route_pattern_id=data.pop('route_pattern_id'),
            route_id=data.pop('route_id'),
            **data
        )


class TripSchema(Schema):
    route_id = mm_fields.Str(required=True)
    service_id = mm_fields.Str(required=True)
    trip_id = mm_fields.Str(required=True)
    trip_headsign = mm_fields.Str()
    trip_short_name = mm_fields.Str()
    direction_id = mm_fields.Int()
    block_id = mm_fields.Str()
    shape_id = mm_fields.Str()
    wheelchair_accessible = EnumField(TripAccessibility)
    trip_route_type = EnumField(RouteType)
    route_pattern_id = mm_fields.Str()
    bikes_allowed = EnumField(TripAccessibility)

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        in_data['wheelchair_accessible'] = numbered_type_enum_key(in_data['wheelchair_accessible'], default_0=True)
        in_data['trip_route_type'] = numbered_type_enum_key(in_data['trip_route_type'])
        in_data['bikes_allowed'] = numbered_type_enum_key(in_data['bikes_allowed'], default_0=True)
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_trip(self, data: Dict, **kwargs) -> Trip:
        return Trip(
            trip_id=data.pop('trip_id'),
            route_id=data.pop('route_id'),
            service_id=data.pop('service_id'),
            **data
        )


class CheckpointSchema(Schema):
    checkpoint_id = mm_fields.Str(required=True)
    checkpoint_name = mm_fields.Str(required=True)

    @post_load
    def make_checkpoint(self, data: Dict, **kwargs) -> Checkpoint:
        return Checkpoint(
            checkpoint_id=data.pop('checkpoint_id'),
            checkpoint_name=data.pop('checkpoint_name')
        )


class StopTimeSchema(Schema):
    trip_id = mm_fields.Str(required=True)
    arrival_time = mm_fields.Int(required=True)
    departure_time = mm_fields.Int(required=True)
    stop_id = mm_fields.Str(required=True)
    stop_sequence = mm_fields.Int(required=True)
    stop_headsign = mm_fields.Str()
    pickup_type = EnumField(PickupDropOffType)
    drop_off_type = EnumField(PickupDropOffType)
    shape_dist_traveled = mm_fields.Float()
    timepoint = mm_fields.Int()
    checkpoint_id = mm_fields.Str()

    @pre_load
    def convert_input(self, in_data: Dict, **kwargs) -> Dict:
        in_data['arrival_time'] = time_as_seconds(in_data['arrival_time'])
        in_data['departure_time'] = time_as_seconds(in_data['departure_time'])
        in_data['pickup_type'] = numbered_type_enum_key(in_data['pickup_type'], default_0=True)
        in_data['drop_off_type'] = numbered_type_enum_key(in_data['drop_off_type'], default_0=True)
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_stop_time(self, data: Dict, **kwargs) -> StopTime:
        return StopTime(
            trip_id=data.pop('trip_id'),
            arrival_time=data.pop('arrival_time'),
            departure_time=data.pop('departure_time'),
            stop_id=data.pop('stop_id'),
            stop_sequence=data.pop('stop_sequence'),
            **data
        )
