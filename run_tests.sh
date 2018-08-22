#!/usr/bin/env bash

docker-compose build && docker-compose run -e FLASK_APP=rest_api tests pytest "$@"