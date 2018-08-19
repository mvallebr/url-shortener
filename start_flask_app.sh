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


export FLASK_APP=rest_api
export FLASK_ENV=development
>&2 echo "Creating Cassandra keyspace and tables"
flask init-db
>&2 echo "Executing flask service"
flask run -h 0.0.0.0  # be visible outside docker
