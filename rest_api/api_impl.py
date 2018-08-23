import json
from flask import make_response, jsonify, request, Blueprint, redirect, Response, current_app, abort
from flask_accept import accept
from rfc3986.exceptions import RFC3986Exception
from urllib.parse import urlparse
from werkzeug.exceptions import NotAcceptable

from rest_api import db, id_cache
from rest_api.url_logic import encode_short_id, decode_short_id, enforce_scheme, validate_url

api = Blueprint("api", __name__)


@api.app_errorhandler(NotAcceptable)
def http_error_handler(error):
    return make_response(jsonify({'error': "HTTP {}".format(error)}), error.code)


@api.app_errorhandler(RFC3986Exception)
def http_error_handler(error):
    return make_response(jsonify({'error': "Bad Request {}".format(error)}), 400)


@api.route('/shorten_url', methods=['POST'])
@accept('application/json')
def shorten_url():
    """
    Example curl call:
    curl -d '{"url": "www.helloworld.com"}' -H "Content-Type: application/json" -H "Accept: application/json" -X \
    POST http://localhost:5000/shorten_url
    :return:
    """
    contents = request.get_json()
    if "url" not in contents:
        abort(400)  # If input json has no url key, then it's a bad request
    original_url = contents["url"]

    original_url = enforce_scheme(original_url, default_scheme=request.scheme)
    validate_url(original_url)

    short_id = id_cache.get_a_new_id()
    db.upsert_short_url(short_id, original_url)
    response = {"shortened_url": "{}{}".format(current_app.config['SHORT_URL_PREFIX'], encode_short_id(short_id))}
    return Response(json.dumps(response), status=201, mimetype='application/json')


@api.route('/<string:short_id>', methods=['GET'])
def get_url(short_id):
    original_url = db.get_original_url(decode_short_id(short_id))
    if original_url is None:
        return make_response(jsonify({'error': 'Not found {}'.format(short_id)}), 404)
    else:
        if not urlparse(original_url).scheme:
            original_url = "http://{}".format(original_url)
        return redirect(original_url, code=301)


@api.route('/')
def hello():
    return "Welcome to url-shortnener"  # TODO show user docs on this endpoint
