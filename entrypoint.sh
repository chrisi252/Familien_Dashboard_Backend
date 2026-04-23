#!/bin/sh
set -e

uv run flask db upgrade
uv run flask sync-widgets

exec uv run gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 "app:create_app()"
