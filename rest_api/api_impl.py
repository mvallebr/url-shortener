import json
import logging
import sys
from urllib.parse import urlparse

from flask import make_response, jsonify, request, Blueprint, redirect, Response, current_app

from rest_api import db

api = Blueprint("api", __name__)


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found {}'.format(error)}), 404)


def _validate(url: str):
    pass


# curl -d '{"url": "www.helloworld.com"}' -H "Content-Type: application/json" -X POST http://localhost:5000/shorten_url
@api.route('/shorten_url', methods=['POST'])
def shorten_url():
    print(request.content_type)
    contents = request.get_json(force=True)
    print(contents)
    original_url = contents["url"]
    db.insert_short_url(123, original_url)
    response = {"shortened_url": "{}123".format(current_app.config['SHORT_URL_PREFIX'])}
    return Response(json.dumps(response), status=201, mimetype='application/json')


@api.route('/<int:short_id>', methods=['GET'])
def get_url(short_id):
    print("short_id = {}".format(short_id), file=sys.stdout)
    current_app.logger.info("short_id = {}".format(short_id))
    original_url = db.get_original_url(short_id)
    current_app.logger.error("original_url = {}".format(original_url))
    print("original_url = {}".format(original_url), file=sys.stdout)
    if original_url is None:
        return make_response(jsonify({'error': 'Not found {}'.format(short_id)}), 404)
    else:
        if not urlparse(original_url).scheme:
            original_url = "http://{}".format(original_url)
        return redirect(original_url, code=301)


@api.route('/')
def hello():
    print("hello", file=sys.stdout)
    return "Hello World! "