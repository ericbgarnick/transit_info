import pytest

from mbta_info.flaskr.database import db as project_db
from mbta_info.flaskr import create_app, set_g, models as mbta_models
from mbta_info.tests import models as test_models


# https://github.com/pytest-dev/pytest/issues/363#issuecomment-406536200
@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def set_test_env(monkeysession):
    monkeysession.setenv("FLASK_ENV", "testing")


@pytest.fixture
def app(set_test_env):
    """Create a Flask app context for the tests."""
    app = create_app()
    with app.app_context():
        set_g()
        project_db.create_all()
        yield app
        project_db.session.close()
        project_db.drop_all()


@pytest.fixture
def db(app):
    return project_db


@pytest.fixture
def geo_stub(db) -> test_models.GeoStub:
    geo_stub_obj = test_models.GeoStub(
        1, 100.1, 200.2
    )
    db.session.add(geo_stub_obj)
    db.session.commit()
    return geo_stub_obj


@pytest.fixture
def test_model(db, geo_stub) -> test_models.TestModel:
    test_model_obj = test_models.TestModel(
        "test1",
        "Test Model",
        test_models.TestType.type_0,
        **{"test_order": 23, "test_dist": 5.5, "geo_stub_id": geo_stub.geo_stub_id}
    )
    db.session.add(test_model_obj)
    db.session.commit()
    return test_model_obj


@pytest.fixture
def agency(db) -> mbta_models.Agency:
    agency_obj = mbta_models.Agency(
        1,
        "Agency",
        "http://www.agency.com",
        mbta_models.TimeZone.America_New_York
    )
    db.session.add(agency_obj)
    db.session.commit()
    return agency_obj


@pytest.fixture
def line(db) -> mbta_models.Line:
    line_obj = mbta_models.Line(
        "Test Line", "Test Line Name"
    )
    db.session.add(line_obj)
    db.session.commit()
    return line_obj
