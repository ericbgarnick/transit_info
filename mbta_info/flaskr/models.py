import enum
import pycountry
import pytz

from mbta_info.flaskr.app import db

TimeZone = enum.Enum('TimeZone', {tz.replace('/', '_'): tz for tz in pytz.all_timezones})
LangCode = enum.Enum('LangCode', {lang.alpha_2: lang.alpha_2
                                  for lang in pycountry.languages
                                  if getattr(lang, 'alpha_2', None)})


class Agency(db.Model):
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
        print("AGENCY TIMEZONE:", repr(self.agency_timezone))

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Agency: {self.agency_name}>'


class Line(db.Model):
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
        print("ROUTE TYPE:", repr(self.route_type))

        for fieldname, value in kwargs.items():
            setattr(self, fieldname, value)

    def __repr__(self):
        return f'<Route: {self.route_id}>'
