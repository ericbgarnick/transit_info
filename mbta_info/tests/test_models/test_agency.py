from mbta_info.flaskr import models as mbta_models


def test_create_minimal_agency(db):
    agency_data = [1, "agency_name", "http://www.agency.com", mbta_models.TimeZone.America_New_York]
    agency = mbta_models.Agency(*agency_data)
    db.session.add(agency)
    db.session.commit()
    assert db.session.query(mbta_models.Agency).count() == 1


def test_create_minimal_agency_again(db):
    agency_data = [1, "agency_name", "http://www.agency.com", mbta_models.TimeZone.America_New_York]
    agency = mbta_models.Agency(*agency_data)
    db.session.add(agency)
    db.session.commit()
    assert db.session.query(mbta_models.Agency).count() == 1
