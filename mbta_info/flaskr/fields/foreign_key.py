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
        self.model_name = model.__name__
        self.error_messages["no_model_data"] = self.EMPTY_TABLE_MESSAGE
        self.error_messages["missing_entry"] = self.MISSING_MODEL_MESSAGE

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Optional[str]:
        model_pk_field = model_utils.pk_field_name(self.model)
        if self.model.query.filter_by(**{model_pk_field: value}).count():
            return value
        elif not self.model.query.count():
            raise self.make_error("no_model_data", model_name=self.model_name)
        else:
            raise self.make_error(
                "missing_entry", model_name=self.model_name, model_id=value
            )

    def is_empty_table_error(self, error: mm.ValidationError) -> bool:
        """Return True if the message for error matches self.EMPTY_TABLE_MESSAGE. Otherwise return False."""
        err_message = self._get_message_from_error(error)
        return err_message == self.EMPTY_TABLE_MESSAGE.format(
            **{"model_name": self.model_name}
        )

    def is_missing_instance_error(self, error: mm.ValidationError) -> bool:
        """Return True if the message for error matches self.MISSING_MODEL_MESSAGE. Otherwise return False."""
        err_message = self._get_message_from_error(error)
        err_message_start = err_message.split(":")[0]  # Drop model id value
        return err_message_start == self.MISSING_MODEL_BASE.format(
            **{"model_name": self.model_name}
        )

    @staticmethod
    def _get_message_from_error(error: mm.ValidationError) -> str:
        return [val[0] for val in error.normalized_messages().values()][0]
