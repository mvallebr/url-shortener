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
        g.url_lookup_stmt = session.prepare("SELECT original_url FROM url_shortener.url_alias WHERE short_id=?")

    return g.cassandra_session


def insert_short_url(short_id: int, original_url: str):
    get_cassandra_session().execute(
        """
        INSERT INTO url_shortener.url_alias (short_id, original_url)
        VALUES (%s, %s)
        """,
        (short_id, original_url)
    )


def get_original_url(short_id: int) -> str:
    result = get_cassandra_session().execute(g.url_lookup_stmt, (short_id,)).current_rows
    return result[0].original_url if len(result) > 0 else None


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Execute the DDL for the keyspace."""
    session = get_cassandra_session()
    with current_app.open_resource('schema.cql', mode='r') as f:
        for stmt in f.read().split(";"):
            stmt = stmt.strip()
            if not stmt:  # skip blank lines
                continue
            logging.info("Executing {}".format(stmt))
            session.execute(stmt)
    click.echo('Initialized the Cassandra keyspace.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.cli.add_command(init_db_command)
