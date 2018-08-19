#!/bin/sh
# This script waits until cassandra is up, creates the key space and tables for tests,
# and then run the flask app. This is only used for the test in docker.

set -e

CASSANDRA_HOST=cassandra

PYTHON_CONNECT_CMD="from cassandra.cluster import Cluster; \
cluster = Cluster(['${CASSANDRA_HOST}']); \
session=cluster.connect()"

# give some seconds for cassandra to start before trying to connect
sleep 7

until python -c "${PYTHON_CONNECT_CMD}"
do
  >&2 echo "Cassandra is unavailable - sleeping"
  sleep 2
done

>&2 echo "Cassandra is up - Creating keyspace"
python -c "${PYTHON_CONNECT_CMD}; \
session.execute(\"DROP KEYSPACE IF EXISTS url_shortener\"); \
session.execute(\"CREATE KEYSPACE url_shortener \
    WITH REPLICATION = {'class' : 'SimpleStrategy','replication_factor' : 1}\
    \"); "

>&2 echo "Creating tables"
# short_id is a 32 bit integer
python -c "${PYTHON_CONNECT_CMD}; \
session.execute(\"CREATE TABLE url_shortener.url_alias (\
    short_id int, original_url text, \
    PRIMARY KEY (short_id)) \
    \"); \
"

>&2 echo "Executing flask service"
exec python url_shortener_rest.py