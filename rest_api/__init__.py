import logging

from flask import Flask

from rest_api.api_impl import api


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    app.config.from_mapping(
        CASSANDRA_ENDPOINTS=['172.18.0.2'],#, 'cassandra'],
        CASSANDRA_KEYSPACE='url_shortener',
        SHORT_URL_PREFIX="http://localhost:5000/",
        INSTANCE_ID=1,  # This parameter should be different for every worker process on every node.
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    app.register_blueprint(api)

    return app
