import typing

import marshmallow as mm
from flask_sqlalchemy import Model

from mbta_info.flaskr import model_utils


class StringForeignKey(mm.fields.String):
    """
    A marshmallow Field for validating string ForeignKey field data
    """

    EMPTY_TABLE_MESSAGE = "No {model_name} data loaded"
    MISSING_MODEL_BASE = "Missing entry for {model_name} id"
    MISSING_MODEL_MESSAGE = MISSING_MODEL_BASE + ": {model_id}"

    def __init__(self, model: Model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.error_messages["no_model_data"] = self.EMPTY_TABLE_MESSAGE
        self.error_messages["missing_entry"] = self.MISSING_MODEL_MESSAGE

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Optional[str]:
        model_pk_field = model_utils.pk_field_name(self.model)
        if self.model.query.filter_by(**{model_pk_field: value}).count():
            return value
        elif not self.model.query.count():
            raise self.make_error("no_model_data", model_name=self.model.__name__)
        else:
            raise self.make_error("missing_entry", route_id=value)

    @staticmethod
    def is_missing_instance_error(error: mm.ValidationError) -> bool:
        """Return True if the message for error matches StringForeignKey.MISSING_MODEL_MESSAGE.
        Otherwise return False."""
        err_message = [val[0] for val in error.normalized_messages().values()][0]
        err_message_start = err_message.split(":")[0]  # Drop route_id value
        return err_message_start == StringForeignKey.MISSING_MODEL_BASE
