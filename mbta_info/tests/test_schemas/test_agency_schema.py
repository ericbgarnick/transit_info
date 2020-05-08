from mbta_info.flaskr import schemas, models as mbta_models


def test_validate_good_data():
    # GIVEN
    agency_data = {
        "agency_id": 1,
        "agency_name": "Agency",
        "agency_url": "http://www.agency.com",
        "agency_timezone": "America/New_York",
        "agency_lang": "EN",
        "agency_phone": "555-555-5555",
    }

    # WHEN
    agency_obj = schemas.AgencySchema().load(agency_data)

    # THEN
    assert isinstance(agency_obj, mbta_models.Agency)
    for key, value in agency_data.items():
        if key == "agency_timezone":
            value = getattr(mbta_models.TimeZone, value.replace("/", "_"))
        elif key == "agency_lang":
            value = getattr(mbta_models.LangCode, value.lower())
        assert getattr(agency_obj, key) == value
