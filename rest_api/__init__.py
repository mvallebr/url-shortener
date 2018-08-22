import os
from flask import Flask

from rest_api.api_impl import api
from rest_api.id_cache import INSTANCE_ID_MASK


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

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
    app.register_blueprint(api)

    if app.config['INSTANCE_ID'] > INSTANCE_ID_MASK:
        raise Exception("Instance id can't be more than {}".format(INSTANCE_ID_MASK))

    return app
