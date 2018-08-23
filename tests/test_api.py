import json
import logging
import pytest

from rest_api import create_app
from rest_api.db import init_db

logging.basicConfig(level=logging.INFO)
REQUEST_HEADERS = {'content-type': 'application/json', 'accept': 'application/json'}


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


def _check_valid_post(client, url: str, expected_short_id: str):
    rv = client.post("/shorten_url", data=json.dumps({"url": url}), headers=REQUEST_HEADERS)
    logging.info("Received post response = {}".format(rv.data))
    assert rv.status_code == 201
    expected = {"shortened_url": "http://localhost:5000/{}".format(expected_short_id)}
    actual = json.loads(rv.data)
    assert expected == actual


def _check_valid_get(client, short_id: str, expected_url: str):
    rv = client.get(short_id)
    logging.info("Received get response = {}".format(rv.data))
    assert rv.status_code == 301
    assert rv.headers['Location'] == expected_url


def test_insert_shorturl_validation_ok(client):
    _check_valid_post(client, url="www.helloworld.com", expected_short_id="AQE=")
    _check_valid_get(client, short_id="/AQE=", expected_url="http://www.helloworld.com")


def test_happy_path_in_sequence(client):
    _check_valid_post(client, url="www.helloworld.com", expected_short_id="AQE=")
    _check_valid_get(client, short_id="/AQE=", expected_url="http://www.helloworld.com")
    _check_valid_post(client, url="https://www.google.com", expected_short_id="AQI=")
    _check_valid_get(client, short_id="AQI=", expected_url="https://www.google.com")
    _check_valid_post(client, url="http://www.uol.com.br", expected_short_id="AQM=")
    _check_valid_get(client, short_id="AQM=", expected_url="http://www.uol.com.br")


def test_post_invalid_headers(client):
    rv = client.post("/shorten_url", data=json.dumps({"wrong_key": "http://valid.url"}),
                     headers={'content-type': 'text/plain', 'accept': 'application/xml'})
    logging.info("Received post response = {}".format(rv.data))
    assert rv.status_code == 406


def test_post_invalid_json(client):
    rv = client.post("/shorten_url", data=json.dumps({"wrong_key": "http://valid.url"}), headers=REQUEST_HEADERS)
    logging.info("Received post response = {}".format(rv.data))
    assert rv.status_code == 400


def test_post_invalid_url(client):
    rv = client.post("/shorten_url", data=json.dumps({"url": "invalid url"}), headers=REQUEST_HEADERS)
    logging.info("Received post response = {}".format(rv.data))
    assert rv.status_code == 400


if __name__ == "__main__":
    pytest.main(["-s", "-v"])
