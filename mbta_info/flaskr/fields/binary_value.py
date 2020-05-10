import marshmallow as mm


class BinaryValue(mm.fields.Integer):
    """
    A marshmallow Field for validating binary values represented by 0 and 1
    """

    INVALID_VALUE = "{value} is not one of the options: [0, 1]"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["invalid_value"] = self.INVALID_VALUE

    def _deserialize(self, value, attr, data, **kwargs) -> int:
        try:
            if type(value) in {str, int, bool} and int(value) in {0, 1}:
                return int(value)
        except ValueError:
            pass

        raise self.make_error("invalid_value", value=value)
