import pytest

from mbta_info.flaskr.models import TimeZone, Agency, Line


@pytest.mark.parametrize(
    "agency_data",
    (
        {
            "agency_id": 1,
            "agency_name": "agency",
            "agency_url": "http://www.agency.com",
            "agency_timezone": TimeZone.America_New_York.value,
            "agency_lang": "en",
            "agency_phone": "111-222-3333"
        },
        {
            "agency_id": 1,
            "agency_name": "agency",
            "agency_url": "http://www.agency.com",
            "agency_timezone": TimeZone.America_New_York.value,
        }
    )
)
def test_create_agency(agency_data):
    init_data = {k: v for k, v in agency_data.items()}
    agency = Agency(
        init_data.pop("agency_id"),
        init_data.pop("agency_name"),
        init_data.pop("agency_url"),
        init_data.pop("agency_timezone"),
        **init_data
    )
    for k, v in agency_data.items():
        assert getattr(agency, k) == v


@pytest.mark.parametrize(
    "line_data",
    (
        {
            "line_id": 1,
            "line_short_name": "line_short",
            "line_long_name": "line_long",
            "line_desc": "description",
            "line_url": "http://www.agency.com/line",
            "line_color": "DA291C",
            "line_text_color": "FFFFFF",
            "line_sort_order": "100"
        },
        {
            "line_id": 1,
            "line_long_name": "line_long",
        }
    )
)
def test_create_line(line_data):
    init_data = {k: v for k, v in line_data.items()}
    line = Line(
        init_data.pop("line_id"),
        init_data.pop("line_long_name"),
        **init_data
    )
    for k, v in line_data.items():
        assert getattr(line, k) == v
