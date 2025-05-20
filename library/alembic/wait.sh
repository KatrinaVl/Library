#!/bin/sh

DB_HOST=${DB_HOST:-database}
DB_PORT=${DB_PORT:-5432}

echo "Waiting for database at $DB_HOST:$DB_PORT..."

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Database is unavailable"
  sleep 2
done

exec "$@"