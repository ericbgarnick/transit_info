import typing

from marshmallow import ValidationError
from marshmallow.fields import String

from mbta_info.flaskr.models import Route


class RouteId(String):
    """
    A marshmallow Field for validating Route id ForeignKey field data
    """

    EMPTY_TABLE_MESSAGE = "No Routes loaded"
    MISSING_ROUTE_MESSAGE = "Missing Route for route_id: {route_id}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["no_routes"] = self.EMPTY_TABLE_MESSAGE
        self.error_messages["missing_route"] = self.MISSING_ROUTE_MESSAGE

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Optional[str]:
        if not isinstance(value, (str, bytes)):
            raise self.make_error("invalid")
        if Route.query.filter_by(route_id=value).count():
            return value
        elif not Route.query.count():
            raise self.make_error("no_routes")
        else:
            raise self.make_error("missing_route", route_id=value)

    @staticmethod
    def is_missing_route_error(error: ValidationError) -> bool:
        """Return True if the message for error matches RouteId.MISSING_ROUTE_MESSAGE. Otherwise return False."""
        try:
            err_message = error.normalized_messages().get("route_id", [""])[0]
            err_message_start = " ".join(
                err_message.split()[:-1]
            )  # Drop route_id value
            return RouteId.MISSING_ROUTE_MESSAGE.startswith(err_message_start)
        except IndexError:
            return False
