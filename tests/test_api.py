import pytest

from rest_api import create_app
from rest_api.db import init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({
        'TESTING': True,
    })

    # create the database and load test data
    with app.app_context():
        init_db() 

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data


if __name__ == "__main__":
    pytest.main(["-s", "-v"])
