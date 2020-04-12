from marshmallow import Schema, fields, pre_load, post_load
from marshmallow_enum import EnumField

from mbta_info.flaskr.models import Agency, Line, Route, TimeZone, LangCode, RouteType, FareClass


class AgencySchema(Schema):
    agency_id = fields.Int(required=True)
    agency_name = fields.Str(required=True)
    agency_url = fields.Url(required=True)
    agency_timezone = EnumField(TimeZone, required=True)
    agency_lang = EnumField(LangCode)
    agency_phone = fields.Str()

    @pre_load
    def convert_input(self, in_data, **kwargs):
        in_data['agency_timezone'] = in_data['agency_timezone'].replace('/', '_')
        in_data['agency_lang'] = in_data.get('agency_lang', '').lower() or None
        return in_data

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
    line_url = fields.Str()
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
    route_url = fields.Str()
    route_color = fields.Str()
    route_text_color = fields.Str()
    route_sort_order = fields.Int()
    route_fare_class = EnumField(FareClass)
    line_id = fields.Str(allow_none=True)

    @pre_load
    def convert_input(self, in_data, **kwargs):
        in_data.pop('listed_route', None)
        in_data['route_fare_class'] = in_data['route_fare_class'].replace(' ', '_').lower()
        in_data['route_type'] = 'type_' + in_data['route_type']
        in_data['line_id'] = in_data['line_id'] or None
        return in_data

    @post_load
    def make_route(self, data, **kwargs):
        return Route(
            data.pop('route_id'),
            data.pop('agency_id'),
            data.pop('route_long_name'),
            data.pop('route_type'),
            **data
        )
