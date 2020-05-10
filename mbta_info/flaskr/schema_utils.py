from typing import Optional

import marshmallow as mm


def timezone_enum_key(raw_tz_name: Optional[str]) -> Optional[str]:
    return raw_tz_name.replace("/", "_") if raw_tz_name else raw_tz_name


def numbered_type_enum_key(
    numeral: Optional[str], default_0: bool = False
) -> Optional[str]:
    if numeral and not numeral.isdecimal():
        raise mm.ValidationError(
            f"numbered_type_enum_key received a non-decimal value: '{numeral}'"
        )
    if default_0:
        numeral = numeral or "0"
    return "type_" + numeral if numeral else None


def time_as_seconds(time_string: str) -> int:
    try:
        hours, minutes, seconds = [int(val) for val in time_string.split(":")]
    except ValueError:
        raise mm.ValidationError(
            f"time_as_seconds cannot convert '{time_string}' to seconds"
        )
    return 3600 * hours + 60 * minutes + seconds


def int_str_to_bool(int_str: str) -> bool:
    """Return True for '1', False for '0'"""
    try:
        return {"1": True, "0": False}[int_str]
    except KeyError:
        raise mm.ValidationError(
            f"int_str_to_bool cannot interpret '{int_str}' as bool"
        )
