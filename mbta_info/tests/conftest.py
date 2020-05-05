import pytest

from mbta_info.flaskr.database import db as project_db
from mbta_info.flaskr import create_app, set_g


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
