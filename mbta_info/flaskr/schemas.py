from typing import Optional

from marshmallow import Schema, fields, pre_load, post_load
from marshmallow_enum import EnumField

from mbta_info.flaskr.models import (
    Agency, Line, Route, TimeZone, LangCode, RouteType, FareClass, LocationType, AccessibilityType, Stop
)


class AgencySchema(Schema):
    agency_id = fields.Int(required=True)
    agency_name = fields.Str(required=True)
    agency_url = fields.Url(required=True)
    agency_timezone = EnumField(TimeZone, required=True)
    agency_lang = EnumField(LangCode)
    agency_phone = fields.Str()

    @pre_load
    def convert_input(self, in_data, **kwargs):
        in_data['agency_timezone'] = timezone_enum_key(in_data['agency_timezone'])
        in_data['agency_lang'] = in_data.get('agency_lang', '').lower()
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_agency(self, data, **kwargs):
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
    def make_line(self, data, **kwargs):
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
    def convert_input(self, in_data, **kwargs):
        in_data.pop('listed_route', None)
        in_data['route_fare_class'] = in_data['route_fare_class'].replace(' ', '_').lower()
        in_data['route_type'] = numbered_type_enum_key(in_data['route_type'])
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_route(self, data, **kwargs):
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
    def convert_input(self, in_data, **kwargs):
        in_data['location_type'] = numbered_type_enum_key(in_data['location_type'], default_0=True)
        in_data['wheelchair_boarding'] = numbered_type_enum_key(in_data['wheelchair_boarding'], default_0=True)
        in_data['vehicle_type'] = numbered_type_enum_key(in_data['vehicle_type'])
        in_data['stop_timezone'] = timezone_enum_key(in_data.get('stop_timezone'))
        return {k: v for k, v in in_data.items() if v}

    @post_load
    def make_stop(self, data, **kwargs):
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


def timezone_enum_key(raw_tz_name: str) -> Optional[str]:
    return raw_tz_name.replace('/', '_') if raw_tz_name else raw_tz_name


def numbered_type_enum_key(numeral: str, default_0: bool = False) -> Optional[str]:
    if default_0:
        numeral = numeral or '0'
    return 'type_' + numeral if numeral else None
