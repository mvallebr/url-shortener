import json

from flask import make_response, jsonify, request, Blueprint

api = Blueprint("api", __name__)


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@api.route('/shorten_url', methods=['POST'])
def shorten_url():
    print(request.content_type)
    params = parse_parameters(request.get_json(force=True))

    return json.dumps(result)


@api.route('/<int:short_id>', methods=['GET'])
def get_url(short_id):
    print(request.content_type)
    params = parse_parameters(request.get_json(force=True))

    return json.dumps(result)


@api.route('/')
def hello():
    return "Hello World! "
