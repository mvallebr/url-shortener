import json
from flask import make_response, jsonify, request, Blueprint, redirect, Response, current_app
from urllib.parse import urlparse

from rest_api import db, id_cache
from rest_api.url_logic import encode_short_id, decode_short_id

api = Blueprint("api", __name__)


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found {}'.format(error)}), 404)


def _validate(url: str):
    pass


# curl -d '{"url": "www.helloworld.com"}' -H "Content-Type: application/json" -X POST http://localhost:5000/shorten_url
@api.route('/shorten_url', methods=['POST'])
def shorten_url():
    contents = request.get_json(force=True)
    original_url = contents["url"]
    short_id = id_cache.get_a_new_id()
    db.upsert_short_url(short_id, original_url)
    response = {"shortened_url": "{}{}".format(current_app.config['SHORT_URL_PREFIX'], encode_short_id(short_id))}
    return Response(json.dumps(response), status=201, mimetype='application/json')


@api.route('/<int:short_id>', methods=['GET'])
def get_url(short_id):
    current_app.logger.debug("short_id = {}  {}".format(short_id, decode_short_id(short_id)))
    original_url = db.get_original_url(decode_short_id(short_id))
    current_app.logger.debug("original_url = {}".format(original_url))
    if original_url is None:
        return make_response(jsonify({'error': 'Not found {}'.format(short_id)}), 404)
    else:
        if not urlparse(original_url).scheme:
            original_url = "http://{}".format(original_url)
        return redirect(original_url, code=301)


@api.route('/')
def hello():
    return "Welcome to url-shortnener"  # TODO show user docs on this endpoint
