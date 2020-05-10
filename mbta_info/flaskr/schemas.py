import logging
import typing

import marshmallow as mm
from marshmallow_enum import EnumField

from mbta_info.flaskr import schema_utils, models as mbta_models
from mbta_info.flaskr.fields import binary_value as bv, foreign_key as fk_fields

logger = logging.getLogger(__name__)

DATE_INPUT_FORMAT = "%Y%m%d"


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
    route_desc = EnumField(mbta_models.RouteDescription)
    route_type = EnumField(mbta_models.RouteType, required=True)
    route_url = mm.fields.Url()
    route_color = mm.fields.Str()
    route_text_color = mm.fields.Str()
    route_sort_order = mm.fields.Int()
    route_fare_class = EnumField(mbta_models.FareClass)
    line_id = fk_fields.StringForeignKey(mbta_models.Line)
    listed_route = bv.BinaryValue(missing=0)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["route_type"] = schema_utils.numbered_type_enum_key(
            in_data["route_type"]
        )
        for key in ("route_desc", "route_fare_class"):
            in_data[key] = in_data[key].replace(" ", "_").lower()

        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_route(self, data: typing.Dict, **kwargs) -> mbta_models.Route:
        return mbta_models.Route(
            data.pop("route_id"),
            data.pop("agency_id"),
            data.pop("route_long_name"),
            data.pop("route_type"),
            data.pop("listed_route"),
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
    parent_station = fk_fields.StringForeignKey(mbta_models.Stop)
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
            in_data[day] = schema_utils.int_str_to_bool(in_data[day])
        # Don't filter out False weekday values
        return {k: v for k, v in in_data.items() if v not in ["", None]}

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


class CalendarAttributeSchema(mm.Schema):
    service_id = fk_fields.StringForeignKey(mbta_models.Calendar, required=True)
    service_description = mm.fields.Str(required=True)
    service_schedule_name = mm.fields.Str(required=True)
    service_schedule_type = EnumField(mbta_models.ServiceScheduleType, required=True)
    service_schedule_typicality = EnumField(mbta_models.ServiceScheduleTypicality)
    rating_start_date = mm.fields.Date(format=DATE_INPUT_FORMAT)
    rating_end_date = mm.fields.Date(format=DATE_INPUT_FORMAT)
    rating_description = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["service_schedule_type"] = in_data["service_schedule_type"].lower()
        in_data["service_schedule_typicality"] = schema_utils.numbered_type_enum_key(
            in_data["service_schedule_typicality"], default_0=True
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_calendar_attribute(
        self, data: typing.Dict, **kwargs
    ) -> mbta_models.CalendarAttribute:
        return mbta_models.CalendarAttribute(
            data.pop("service_id"),
            data.pop("service_description"),
            data.pop("service_schedule_name"),
            data.pop("service_schedule_type"),
            **data,
        )


class CalendarDateSchema(mm.Schema):
    service_id = fk_fields.StringForeignKey(mbta_models.Calendar, required=True)
    date = mm.fields.Date(format=DATE_INPUT_FORMAT, required=True)
    exception_type = EnumField(mbta_models.DateExceptionType, required=True)
    holiday_name = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["exception_type"] = schema_utils.numbered_type_enum_key(
            in_data["exception_type"]
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_calendar_date(
        self, data: typing.Dict, **kwargs
    ) -> mbta_models.CalendarDate:
        return mbta_models.CalendarDate(
            data.pop("service_id"),
            data.pop("date"),
            data.pop("exception_type"),
            **data,
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
    route_id = fk_fields.StringForeignKey(mbta_models.Route, required=True)
    direction_id = bv.BinaryValue(required=True)
    direction = EnumField(mbta_models.DirectionOption, required=True)
    direction_destination = mm.fields.Str(required=True)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["direction"] = in_data["direction"].lower()
        return {k: v for k, v in in_data.items() if v}

    def load(self, *args, **kwargs) -> typing.Optional[mbta_models.Direction]:
        """Load direction data, skipping rows that reference non-existent Routes"""
        try:
            return super().load(*args, **kwargs)
        except mm.ValidationError as ve:
            # self.route_id doesn't exist when a ValidationError has occurred
            string_fk_field = fk_fields.StringForeignKey(mbta_models.Route)
            if string_fk_field.is_missing_instance_error(ve):
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
    route_id = fk_fields.StringForeignKey(mbta_models.Route, required=True)
    direction_id = bv.BinaryValue()
    route_pattern_name = mm.fields.Str()
    route_pattern_time_desc = mm.fields.Str()
    route_pattern_typicality = EnumField(mbta_models.RoutePatternTypicality)
    route_pattern_sort_order = mm.fields.Int()
    representative_trip_id = mm.fields.Str()

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["route_pattern_typicality"] = schema_utils.numbered_type_enum_key(
            in_data["route_pattern_typicality"]
        )
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
    route_id = fk_fields.StringForeignKey(mbta_models.Route, required=True)
    service_id = fk_fields.StringForeignKey(mbta_models.Calendar, required=True)
    trip_id = mm.fields.Str(required=True)
    trip_headsign = mm.fields.Str()
    trip_short_name = mm.fields.Str()
    direction_id = bv.BinaryValue()
    block_id = mm.fields.Str()
    shape_id = mm.fields.Str()
    wheelchair_accessible = EnumField(mbta_models.TripAccessibility)
    trip_route_type = EnumField(mbta_models.RouteType)
    route_pattern_id = fk_fields.StringForeignKey(mbta_models.RoutePattern)
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

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_checkpoint(self, data: typing.Dict, **kwargs) -> mbta_models.Checkpoint:
        return mbta_models.Checkpoint(
            checkpoint_id=data.pop("checkpoint_id"),
            checkpoint_name=data.pop("checkpoint_name"),
        )


class StopTimeSchema(mm.Schema):
    trip_id = fk_fields.StringForeignKey(mbta_models.Trip, required=True)
    arrival_time = mm.fields.Int(required=True)
    departure_time = mm.fields.Int(required=True)
    stop_id = fk_fields.StringForeignKey(mbta_models.Stop, required=True)
    stop_sequence = mm.fields.Int(required=True)
    stop_headsign = mm.fields.Str()
    pickup_type = EnumField(mbta_models.PickupDropOffType)
    drop_off_type = EnumField(mbta_models.PickupDropOffType)
    shape_dist_traveled = mm.fields.Float()
    timepoint = bv.BinaryValue()
    checkpoint_id = fk_fields.StringForeignKey(mbta_models.Checkpoint)

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


class LinkedDatasetSchema(mm.Schema):
    url = mm.fields.Url(required=True)
    trip_updates = bv.BinaryValue(required=True)
    vehicle_positions = bv.BinaryValue(required=True)
    service_alerts = bv.BinaryValue(required=True)
    authentication_type = EnumField(mbta_models.AuthenticationType, required=True)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        in_data["authentication_type"] = schema_utils.numbered_type_enum_key(
            in_data["authentication_type"]
        )
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_linked_dataset(
        self, data: typing.Dict, **kwargs
    ) -> mbta_models.LinkedDataset:
        return mbta_models.LinkedDataset(
            url=data.pop("url"),
            trip_updates=data.pop("trip_updates"),
            vehicle_positions=data.pop("vehicle_positions"),
            service_alerts=data.pop("service_alerts"),
            authentication_type=data.pop("authentication_type"),
        )


class MultiRouteTripSchema(mm.Schema):
    added_route_id = fk_fields.StringForeignKey(mbta_models.Route, required=True)
    trip_id = fk_fields.StringForeignKey(mbta_models.Trip, required=True)

    @mm.pre_load
    def convert_input(self, in_data: typing.Dict, **kwargs) -> typing.Dict:
        return {k: v for k, v in in_data.items() if v}

    @mm.post_load
    def make_multi_route_trip(self, data: typing.Dict, **kwargs) -> mbta_models.MultiRouteTrip:
        return mbta_models.MultiRouteTrip(
            added_route_id=data.pop("added_route_id"),
            trip_id=data.pop("trip_id"),
        )
