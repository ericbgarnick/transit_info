import marshmallow as mm


class BinaryValue(mm.fields.Field):
    """
    A marshmallow Field for validating binary values represented by 0 and 1
    """

    INVALID_VALUE = "{value} cannot be interpreted as one of: [0, 1]"
    ACCEPTED_TYPES = (int, str, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["invalid_value"] = self.INVALID_VALUE

    def _deserialize(self, value, attr, data, **kwargs) -> int:
        try:
            if type(value) in self.ACCEPTED_TYPES and int(value) in (0, 1):
                return int(value)
        except (TypeError, ValueError, OverflowError):
            pass

        raise self.make_error("invalid_value", value=value)
