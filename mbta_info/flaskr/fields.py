import typing

import marshmallow as mm

from mbta_info.flaskr import models


class RouteId(mm.fields.String):
    """
    A marshmallow Field for validating Route id ForeignKey field data
    """

    EMPTY_TABLE_MESSAGE = "No Routes loaded"
    MISSING_ROUTE_BASE = "Missing Route for route_id"
    MISSING_ROUTE_MESSAGE = MISSING_ROUTE_BASE + ": {route_id}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["no_routes"] = self.EMPTY_TABLE_MESSAGE
        self.error_messages["missing_route"] = self.MISSING_ROUTE_MESSAGE

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Optional[str]:
        if models.Route.query.filter_by(route_id=value).count():
            return value
        elif not models.Route.query.count():
            raise self.make_error("no_routes")
        else:
            raise self.make_error("missing_route", route_id=value)

    @staticmethod
    def is_missing_route_error(error: mm.ValidationError) -> bool:
        """Return True if the message for error matches RouteId.MISSING_ROUTE_MESSAGE. Otherwise return False."""
        err_message = [val[0] for val in error.normalized_messages().values()][0]
        err_message_start = err_message.split(":")[0]  # Drop route_id value
        return err_message_start == RouteId.MISSING_ROUTE_BASE
