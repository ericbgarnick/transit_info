from typing import Optional, Dict

from marshmallow import Schema, fields, pre_load, post_load
from marshmallow_enum import EnumField

from mbta_info.flaskr.models import (
    Agency, Line, Route, TimeZone, LangCode, RouteType, FareClass, LocationType, AccessibilityType, Stop, Calendar,
    Shape
)


class AgencySchema(Schema):
    agency_id = fields.Int(required=True)
    agency_name = fields.Str(required=True)
    agency_url = fields.Url(required=True)
    agency_timezone = EnumField(TimeZone, required=True)
    agency_lang = EnumField(LangCode)
    agency_phone = fields.Str()

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
    line_id = fields.Str(required=True)
    line_short_name = fields.Str()
    line_long_name = fields.Str(required=True)
    line_desc = fields.Str()
    line_url = fields.Url()
    line_color = fields.Str()
    line_text_color = fields.Str()
    line_sort_order = fields.Int()

    @post_load
    def make_line(self, data: Dict, **kwargs) -> Line:
        return Line(
            data.pop('line_id'),
            data.pop('line_long_name'),
            **data
        )


class RouteSchema(Schema):
    route_id = fields.Str(required=True)
    agency_id = fields.Int(required=True)
    route_short_name = fields.Str()
    route_long_name = fields.Str(required=True)
    route_desc = fields.Str()
    route_type = EnumField(RouteType, required=True)
    route_url = fields.Url()
    route_color = fields.Str()
    route_text_color = fields.Str()
    route_sort_order = fields.Int()
    route_fare_class = EnumField(FareClass)
    line_id = fields.Str()

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
    stop_id = fields.Str(required=True)
    stop_code = fields.Str()
    stop_name = fields.Str()
    tts_stop_name = fields.Str()
    stop_desc = fields.Str()
    platform_code = fields.Str()
    platform_name = fields.Str()
    stop_lat = fields.Float()
    stop_lon = fields.Float()
    zone_id = fields.Str()
    stop_address = fields.Str()
    stop_url = fields.Url()
    level_id = fields.Str()
    location_type = EnumField(LocationType)
    parent_station = fields.Str()
    wheelchair_boarding = EnumField(AccessibilityType)
    municipality = fields.Str()
    on_street = fields.Str()
    at_street = fields.Str()
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

    service_id = fields.Str(required=True)
    monday = fields.Bool(required=True)
    tuesday = fields.Bool(required=True)
    wednesday = fields.Bool(required=True)
    thursday = fields.Bool(required=True)
    friday = fields.Bool(required=True)
    saturday = fields.Bool(required=True)
    sunday = fields.Bool(required=True)
    start_date = fields.Date(format=DATE_INPUT_FORMAT, required=True)
    end_date = fields.Date(format=DATE_INPUT_FORMAT, required=True)

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
    shape_id = fields.Str(required=True)
    shape_pt_lat = fields.Float(required=True)
    shape_pt_lon = fields.Float(required=True)
    shape_pt_sequence = fields.Int(required=True)
    shape_dist_traveled = fields.Float()

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


def timezone_enum_key(raw_tz_name: str) -> Optional[str]:
    return raw_tz_name.replace('/', '_') if raw_tz_name else raw_tz_name


def numbered_type_enum_key(numeral: str, default_0: bool = False) -> Optional[str]:
    if default_0:
        numeral = numeral or '0'
    return 'type_' + numeral if numeral else None
