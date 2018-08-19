import logging

import click
from cassandra.cluster import Cluster
from flask import current_app, g
from flask.cli import with_appcontext


def get_cassandra_session():
    if 'cassandra_session' not in g:
        cluster = Cluster(current_app.config['CASSANDRA_ENDPOINTS'])  # current_app.config['CASSANDRA_ENDPOINTS']
        session = cluster.connect(current_app.config['CASSANDRA_KEYSPACE'])
        g.cassandra_session = session

    return g.cassandra_session


def init_cassandra_keyspace():
    session = get_cassandra_session()

    with current_app.open_resource('schema.cql', mode='r') as f:
        for stmt in f.read().split(";"):
            stmt = stmt.strip()
            if not stmt:  # skip blank lines
                continue
            logging.info("Executing {}".format(stmt))
            session.execute(stmt)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_cassandra_keyspace()
    click.echo('Initialized the Cassandra keyspace.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.cli.add_command(init_db_command)
