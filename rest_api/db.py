import click
import logging
from cassandra.cluster import Cluster
from cassandra.policies import TokenAwarePolicy, DCAwareRoundRobinPolicy
from flask import current_app, g
from flask.cli import with_appcontext

LOAD_BALANCING_POLICY = TokenAwarePolicy(DCAwareRoundRobinPolicy())


def get_cassandra_session():
    if 'cassandra_session' not in g:
        cluster = Cluster(current_app.config['CASSANDRA_ENDPOINTS'], load_balancing_policy=LOAD_BALANCING_POLICY)
        session = cluster.connect(current_app.config['CASSANDRA_KEYSPACE'])
        g.cassandra_session = session
        g.url_lookup_stmt = session.prepare("SELECT original_url FROM url_shortener.url_alias WHERE short_id=?")
        g.c_id_lookup_stmt = session.prepare("SELECT current_id FROM url_shortener.instance_seq WHERE instance_id=?")

    return g.cassandra_session


def upsert_current_id(instance_id: int, current_id: int):
    get_cassandra_session().execute(
        """
        INSERT INTO url_shortener.instance_seq (instance_id, current_id)
        VALUES (%s, %s)
        """,
        (instance_id, current_id)
    )


def get_current_id(instance_id: int):
    result = get_cassandra_session().execute(g.c_id_lookup_stmt, (instance_id,)).current_rows
    return result[0].current_id if len(result) > 0 else 0


def upsert_short_url(short_id: int, original_url: str):
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


def init_db():
    cluster = Cluster(current_app.config['CASSANDRA_ENDPOINTS'], load_balancing_policy=LOAD_BALANCING_POLICY)
    session = cluster.connect()
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
    """Execute the DDL for the keyspace."""
    init_db()
    click.echo('Initialized the Cassandra keyspace.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.cli.add_command(init_db_command)
