import logging
import typing

import marshmallow as mm
from marshmallow_enum import EnumField

from mbta_info.flaskr import models as mbta_models
from mbta_info.flaskr import schema_utils
from mbta_info.flaskr import fields as mbta_fields

logger = logging.getLogger(__name__)


class AgencySchema(mm.Schema):
    agency_id = mm.fields.Int(required=True)
    agency_name = mm.fields.Str(required=True)
    agency_url = mm.fields.Url(required=True)
    agency_timezone = EnumField(mbta_models.TimeZone, required=True)
    agency_lang = EnumField(mbta_models.LangCode)
    agency_phone = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["agency_timezone"] = schema_utils.timezone_enum_key(
            in_data["agency_timezone"]
        )
        in_data["agency_lang"] = in_data.get("agency_lang", "").lower()
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_agency(self, data: typing.Dict, **kwargs) -> mbta_models.Agency:
        return mbta_models.Agency(
            data.pop("agency_id"),
            data.pop("agency_name"),
            data.pop("agency_url"),
            data.pop("agency_timezone"),
            **data,
        )


class LineSchema(mm.Schema):
    line_id = mm.fields.Str(required=True)
    line_short_name = mm.fields.Str()
    line_long_name = mm.fields.Str(required=True)
    line_desc = mm.fields.Str()
    line_url = mm.fields.Url()
    line_color = mm.fields.Str()
    line_text_color = mm.fields.Str()
    line_sort_order = mm.fields.Int()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_line(self, data: typing.Dict, **kwargs) -> mbta_models.Line:
        return mbta_models.Line(data.pop("line_id"), data.pop("line_long_name"), **data)


class RouteSchema(mm.Schema):
    route_id = mm.fields.Str(required=True)
    agency_id = mm.fields.Int(required=True)
    route_short_name = mm.fields.Str()
    route_long_name = mm.fields.Str(required=True)
    route_desc = mm.fields.Str()
    route_type = EnumField(mbta_models.RouteType, required=True)
    route_url = mm.fields.Url()
    route_color = mm.fields.Str()
    route_text_color = mm.fields.Str()
    route_sort_order = mm.fields.Int()
    route_fare_class = EnumField(mbta_models.FareClass)
    line_id = mbta_fields.StringForeignKey(mbta_models.Line)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data.pop("listed_route", None)
        in_data["route_fare_class"] = (
            in_data["route_fare_class"].replace(" ", "_").lower()
        )
        in_data["route_type"] = schema_utils.numbered_type_enum_key(
            in_data["route_type"]
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_route(self, data: typing.Dict, **kwargs) -> mbta_models.Route:
        return mbta_models.Route(
            data.pop("route_id"),
            data.pop("agency_id"),
            data.pop("route_long_name"),
            data.pop("route_type"),
            **data,
        )


class StopSchema(mm.Schema):
    stop_id = mm.fields.Str(required=True)
    stop_code = mm.fields.Str()
    stop_name = mm.fields.Str()
    tts_stop_name = mm.fields.Str()
    stop_desc = mm.fields.Str()
    platform_code = mm.fields.Str()
    platform_name = mm.fields.Str()
    stop_lat = mm.fields.Float()
    stop_lon = mm.fields.Float()
    zone_id = mm.fields.Str()
    stop_address = mm.fields.Str()
    stop_url = mm.fields.Url()
    level_id = mm.fields.Str()
    location_type = EnumField(mbta_models.LocationType)
    parent_station = mbta_fields.StringForeignKey(mbta_models.Stop)
    wheelchair_boarding = EnumField(mbta_models.AccessibilityType)
    municipality = mm.fields.Str()
    on_street = mm.fields.Str()
    at_street = mm.fields.Str()
    vehicle_type = EnumField(mbta_models.RouteType)
    stop_timezone = EnumField(mbta_models.TimeZone)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["location_type"] = schema_utils.numbered_type_enum_key(
            in_data["location_type"], default_0=True
        )
        in_data["wheelchair_boarding"] = schema_utils.numbered_type_enum_key(
            in_data["wheelchair_boarding"], default_0=True
        )
        in_data["vehicle_type"] = schema_utils.numbered_type_enum_key(
            in_data["vehicle_type"]
        )
        in_data["stop_timezone"] = schema_utils.timezone_enum_key(
            in_data.get("stop_timezone")
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_stop(self, data: typing.Dict, **kwargs) -> mbta_models.Stop:
        try:
            lon = data.pop("stop_lon")
            lat = data.pop("stop_lat")
            data["stop_lonlat"] = f"POINT({lon} {lat})"
        except KeyError:
            pass
        return mbta_models.Stop(data.pop("stop_id"), **data)


class CalendarSchema(mm.Schema):
    DATE_INPUT_FORMAT = "%Y%m%d"

    service_id = mm.fields.Str(required=True)
    monday = mm.fields.Bool(required=True)
    tuesday = mm.fields.Bool(required=True)
    wednesday = mm.fields.Bool(required=True)
    thursday = mm.fields.Bool(required=True)
    friday = mm.fields.Bool(required=True)
    saturday = mm.fields.Bool(required=True)
    sunday = mm.fields.Bool(required=True)
    start_date = mm.fields.Date(format=DATE_INPUT_FORMAT, required=True)
    end_date = mm.fields.Date(format=DATE_INPUT_FORMAT, required=True)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            in_data[day] = bool(int(in_data[day]))
        return in_data

    @mm.post_load
    def make_calendar(self, data: typing.Dict, **kwargs) -> mbta_models.Calendar:
        return mbta_models.Calendar(
            data.pop("service_id"),
            data.pop("monday"),
            data.pop("tuesday"),
            data.pop("wednesday"),
            data.pop("thursday"),
            data.pop("friday"),
            data.pop("saturday"),
            data.pop("sunday"),
            data.pop("start_date"),
            data.pop("end_date"),
        )


class ShapeSchema(mm.Schema):
    shape_id = mm.fields.Str(required=True)
    shape_pt_lat = mm.fields.Float(required=True)
    shape_pt_lon = mm.fields.Float(required=True)
    shape_pt_sequence = mm.fields.Int(required=True)
    shape_dist_traveled = mm.fields.Float()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_shape(self, data: typing.Dict, **kwargs) -> mbta_models.Shape:
        return mbta_models.Shape(
            data.pop("shape_id"),
            data.pop("shape_pt_lon"),
            data.pop("shape_pt_lat"),
            data.pop("shape_pt_sequence"),
            **data,
        )


class DirectionSchema(mm.Schema):
    route_id = mbta_fields.StringForeignKey(mbta_models.Route, required=True)
    direction_id = mm.fields.Int(required=True)
    direction = mm.fields.Str(required=True)
    direction_destination = mm.fields.Str(required=True)

    def load(self, *args, **kwargs) -> typing.Optional[mbta_models.Direction]:
        """Load direction data, skipping rows that reference non-existent Routes"""
        try:
            return super().load(*args, **kwargs)
        except mm.ValidationError as ve:
            if self.route_id.is_missing_instance_error(ve):
                logger.info(ve.normalized_messages())
                return None
            else:
                raise ve

    @mm.post_load
    def make_direction(self, data: typing.Dict, **kwargs) -> mbta_models.Direction:
        return mbta_models.Direction(
            route_id=data.pop("route_id"),
            direction_id=data.pop("direction_id"),
            direction=data.pop("direction"),
            direction_destination=data.pop("direction_destination"),
        )


class RoutePatternSchema(mm.Schema):
    route_pattern_id = mm.fields.Str(required=True)
    route_id = mm.fields.Str(required=True)
    direction_id = mm.fields.Int()
    route_pattern_name = mm.fields.Str()
    route_pattern_time_desc = mm.fields.Str()
    route_pattern_typicality = mm.fields.Int()
    route_pattern_sort_order = mm.fields.Int()
    representative_trip_id = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_route_pattern(
        self, data: typing.Dict, **kwargs
    ) -> mbta_models.RoutePattern:
        return mbta_models.RoutePattern(
            route_pattern_id=data.pop("route_pattern_id"),
            route_id=data.pop("route_id"),
            **data,
        )


class TripSchema(mm.Schema):
    route_id = mm.fields.Str(required=True)
    service_id = mm.fields.Str(required=True)
    trip_id = mm.fields.Str(required=True)
    trip_headsign = mm.fields.Str()
    trip_short_name = mm.fields.Str()
    direction_id = mm.fields.Int()
    block_id = mm.fields.Str()
    shape_id = mm.fields.Str()
    wheelchair_accessible = EnumField(mbta_models.TripAccessibility)
    trip_route_type = EnumField(mbta_models.RouteType)
    route_pattern_id = mm.fields.Str()
    bikes_allowed = EnumField(mbta_models.TripAccessibility)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["wheelchair_accessible"] = schema_utils.numbered_type_enum_key(
            in_data["wheelchair_accessible"], default_0=True
        )
        in_data["trip_route_type"] = schema_utils.numbered_type_enum_key(
            in_data["trip_route_type"]
        )
        in_data["bikes_allowed"] = schema_utils.numbered_type_enum_key(
            in_data["bikes_allowed"], default_0=True
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_trip(self, data: typing.Dict, **kwargs) -> mbta_models.Trip:
        return mbta_models.Trip(
            trip_id=data.pop("trip_id"),
            route_id=data.pop("route_id"),
            service_id=data.pop("service_id"),
            **data,
        )


class CheckpointSchema(mm.Schema):
    checkpoint_id = mm.fields.Str(required=True)
    checkpoint_name = mm.fields.Str(required=True)

    @mm.post_load
    def make_checkpoint(self, data: typing.Dict, **kwargs) -> mbta_models.Checkpoint:
        return mbta_models.Checkpoint(
            checkpoint_id=data.pop("checkpoint_id"),
            checkpoint_name=data.pop("checkpoint_name"),
        )


class StopTimeSchema(mm.Schema):
    trip_id = mm.fields.Str(required=True)
    arrival_time = mm.fields.Int(required=True)
    departure_time = mm.fields.Int(required=True)
    stop_id = mm.fields.Str(required=True)
    stop_sequence = mm.fields.Int(required=True)
    stop_headsign = mm.fields.Str()
    pickup_type = EnumField(mbta_models.PickupDropOffType)
    drop_off_type = EnumField(mbta_models.PickupDropOffType)
    shape_dist_traveled = mm.fields.Float()
    timepoint = mm.fields.Int()
    checkpoint_id = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["arrival_time"] = schema_utils.time_as_seconds(in_data["arrival_time"])
        in_data["departure_time"] = schema_utils.time_as_seconds(
            in_data["departure_time"]
        )
        in_data["pickup_type"] = schema_utils.numbered_type_enum_key(
            in_data["pickup_type"], default_0=True
        )
        in_data["drop_off_type"] = schema_utils.numbered_type_enum_key(
            in_data["drop_off_type"], default_0=True
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_stop_time(self, data: typing.Dict, **kwargs) -> mbta_models.StopTime:
        return mbta_models.StopTime(
            trip_id=data.pop("trip_id"),
            arrival_time=data.pop("arrival_time"),
            departure_time=data.pop("departure_time"),
            stop_id=data.pop("stop_id"),
            stop_sequence=data.pop("stop_sequence"),
            **data,
        )
