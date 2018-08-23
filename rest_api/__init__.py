import os
from flask import Flask, make_response, jsonify
from rfc3986.exceptions import RFC3986Exception
from werkzeug.exceptions import NotAcceptable

from rest_api import id_cache
from rest_api.api_impl import api
from rest_api.url_logic import INSTANCE_ID_MASK

# Register error handlers for expected errors
ERROR_HANDLERS = [(NotAcceptable, "", 406), (406, "", 406), (404, "Not Found", 404),
                  (Exception, "Internal Server Error", 500), (RFC3986Exception, "Bad Request", 400), ]


def register_default_error_handlers(app):
    for code_or_exception, description, code in ERROR_HANDLERS:
        app.register_error_handler(code_or_exception,
                                   lambda e: make_response(jsonify({'error': "{} {}".format(description, e)}), code))



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # register_default_error_handlers(app)

    # default config
    app.config.from_mapping(
        CASSANDRA_ENDPOINTS=[os.environ.get('CASSANDRA_ENDPOINT', 'cassandra')],
        CASSANDRA_KEYSPACE='url_shortener',
        SHORT_URL_PREFIX="http://localhost:5000/",
        INSTANCE_ID=1,  # This parameter should be different for every worker process on every node.
    )

    if test_config is None:
        # in prod, config.py would be used instead
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)
    id_cache.cache.clear()  # Make sure cache is cleared
    app.register_blueprint(api)

    if app.config['INSTANCE_ID'] > INSTANCE_ID_MASK:
        raise Exception("Instance id can't be more than {}".format(INSTANCE_ID_MASK))

    return app
