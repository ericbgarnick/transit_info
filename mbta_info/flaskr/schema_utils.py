from typing import Optional


def timezone_enum_key(raw_tz_name: Optional[str]) -> Optional[str]:
    return raw_tz_name.replace("/", "_") if raw_tz_name else raw_tz_name


def numbered_type_enum_key(numeral: Optional[str], default_0: bool = False) -> Optional[str]:
    if numeral and not numeral.isdecimal():
        raise TypeError("numbered_type_enum_key received a non-numeric value")
    if default_0:
        numeral = numeral or "0"
    return "type_" + numeral if numeral else None


def time_as_seconds(time_string: str) -> int:
    hours, minutes, seconds = [int(val) for val in time_string.split(":")]
    return 3600 * hours + 60 * minutes + seconds
