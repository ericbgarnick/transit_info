import pytest

from mbta_info.flaskr.database import db
from mbta_info.flaskr import create_app


@pytest.fixture(scope='session')
def app():
    """Create a Flask app context for the tests."""
    app = create_app("test")
    with app.app_context():
        db.create_all()
        yield app
        db.session.close()
        db.drop_all()
