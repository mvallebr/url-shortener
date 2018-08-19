# from cassandra.cluster import Cluster

from flask import Flask

#
# cluster = Cluster(['cassandra'])
# session = cluster.connect('url_shortener')
# app = Flask(__name__)
#
# import rest_api.api_impl
import rest_api
from rest_api.api_impl import api


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        CASSANDRA_ENDPOINTS=['cassandra'],
        CASSANDRA_KEYSPACE='url_shortener',
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
