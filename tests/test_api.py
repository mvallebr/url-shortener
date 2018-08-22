import json
import logging

import pytest

from rest_api import create_app
from rest_api.db import init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    _app = create_app({
        'TESTING': True,
        'DEBUG': True,
    })

    # create the database and load test data
    with _app.app_context():
        init_db()

    yield _app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_root_endpoint(client):
    rv = client.get('/')
    assert b'Welcome to url-shortnener' == rv.data


def test_insert_shorturl_validation_ok(client):
    rv = client.post("/shorten_url", data='{"url": "www.helloworld.com"}')
    assert rv.status_code == 201
    print("received post data = {}".format(rv.data))
    expected = {"shortened_url": "http://localhost:5000/AQE="}
    actual = json.loads(rv.data)

    assert expected == actual

    rv2 = client.get("/AQE=")
    assert rv2.status_code == 301
    assert rv2.headers['Location'] == "http://www.helloworld.com"


if __name__ == "__main__":
    pytest.main(["-s", "-v"])
